let currentRegion = "";
let currentTech = "";

let chartZoomStart = {};
let chartZoomEnd = {};

const nodes = JSON.parse(document.getElementById("nodes").innerText);

// Called when a region button is clicked
async function showHiddenDiv(region, button) {
    const parentContainer = button.closest(".results__region-container");
    const isAlreadySelected = parentContainer.classList.contains("selected");

    // Deselect all containers and buttons
    document.querySelectorAll(".results__region-container").forEach(container => {
        container.classList.remove("selected");
        const btn = container.querySelector(".select-button");
        if (btn) {
            btn.classList.remove("selected");
            btn.textContent = "Auswählen";
        }

    showDropdownBasicSolution(region);
    });

    const hiddenDiv = document.querySelector(".hidden-div");

    if (isAlreadySelected) {
        // If the same card is clicked again, toggle it off
        hiddenDiv.style.display = "none";
        currentRegion = null;
        return;
    }

    // Select the clicked container and button
    parentContainer.classList.add("selected");
    button.classList.add("selected");
    button.textContent = "Ausgewählt";
    hiddenDiv.style.display = "block";

    try {
        await loadFlowsChart(region, "electricity");
        await loadFlowsChart(region, "hydrogen");
        await loadBasicData(region);
    } catch (error) {
        console.error("Error in showHiddenDiv:", error);
    }

    currentRegion = region;
    await initializeTechnologySelect();
    loadRanges();
}

document.addEventListener("DOMContentLoaded", () => {
    const costDropdown = document.getElementById("technologySelect");
    if (costDropdown) {
        costDropdown.addEventListener("change", function () {
            const selectedType = this.value;
            loadCostCapacityData(selectedType);
        });
        if (costDropdown.options.length > 0) {
            currentTech = costDropdown.options[0].value;
            loadCostCapacityData(currentTech);
        }
    }

    const demandDropdown = document.getElementById("demand-technologySelect");
    if (demandDropdown) {
        demandDropdown.addEventListener("change", function () {
            const selectedType = this.value;
            loadDemandData(selectedType);
            loadDemandCapacityData(selectedType);
        });
        if (demandDropdown.options.length > 0) {
            currentTech = demandDropdown.options[0].value;
            loadDemandData(currentTech);
            loadDemandCapacityData(currentTech);
        }
    }
});

function getOrCreateChart(domElement) {
    let chart = echarts.getInstanceByDom(domElement);
    if (chart) {
        chart.clear();
    } else {
        chart = echarts.init(domElement, null, { renderer: "svg" });
    }
    return chart;
}

function removeChart(domElement) {
    let chart = echarts.getInstanceByDom(domElement);
    if (chart) {
        chart.clear();
    }
}

async function loadFlowsChart(chartType, region) {
    const url = `${window.location.origin}/explorer/chart/flow_chart?type=${encodeURIComponent(chartType)}&region=${encodeURIComponent(region)}`;
    try {
        const response = await fetch(url, {
            method: "GET",
            mode: "cors",
            headers: { "Accept": "application/json" },
            credentials: "same-origin"
        });
        if (!response.ok) throw new Error("Network error: " + response.status);
        const jsonObj = await response.json();
        const hydroData = jsonObj.flow_data.filter(d => d.carrier === "h2");
        const electricityData = jsonObj.flow_data.filter(d => d.carrier === "electricity");
        createFlowChart(electricityData, "electricity", "electricity-chart");
        createFlowChart(hydroData, "hydrogen", "hydrogen-chart");
    } catch (error) {
        console.error("Error loading flow chart:", error);
    }
}

function createFlowChart(data, resource, chartID) {
    if (!data || data.length === 0) {
      const resource_de = resource === "hydrogen" ? "Wasserstoff" : "Strom";
      const chartDiv = document.getElementById(chartID);
      const wrapper = chartDiv.parentNode;
      const msgClass = `${chartID}_msg`;
      document.querySelectorAll(`.${msgClass}`).forEach(function(div) {
        div.remove();
      });
      const msg = document.createElement("div");
      msg.classList.add(msgClass);
      msg.textContent = "Aktuell gibt es keine Daten für " + resource_de + ".";
      msg.style.textAlign = "center";
      msg.style.padding = "1em";
      msg.style.fontSize = "1.1em";
      msg.style.color = "#555";
      wrapper.insertBefore(msg, chartDiv);
      return;
    }

    const chart = getOrCreateChart(document.getElementById(chartID));
    let values = data.map(d => d.value);
    let minEnergy = Math.min(...values);
    let maxEnergy = Math.max(...values);
    function scaleLineWidth(value) {
        let diff = maxEnergy - minEnergy;
        return diff === 0 ? 4 : 1 + ((value - minEnergy) / diff) * 7;
    }
    let gradientColors = resource === "hydrogen" ?
        [{ offset: 0, color: "#feb1b1" }, { offset: 1, color: "#c34747" }] :
        [{ offset: 0, color: "#a2edbd" }, { offset: 1, color: "#20a54f" }];
    const links  = data.map(d => ({
          source: d.source,
          target: d.target,
          value:  d.value,
          lineStyle: { width: scaleLineWidth(d.value) }
        }));
    let option = {
        title: { text: data.title || "Flussdiagramm", left: "center" },
        tooltip: {
            trigger: "item",
            formatter: function (params) {
                return params.dataType === "edge" ?
                    `$${params.data.source} → $${params.data.target}: $${params.data.value} MWh` : params.name;
            }
        },
        series: [{
            type: "graph",
            layout: "none",
            force: { repulsion: 300, edgeLength: [50, 200] },
            roam: true,
            label: { show: true, position: "right", fontSize: 20 },
            edgeSymbol: ["none", "arrow"],
            edgeSymbolSize: 10,
            lineStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 1, 0, gradientColors),
                curveness: 0.2,
                opacity: 0.8
            },
            data: nodes,
            links: links,
            emphasis: { focus: "adjacency" }
        }]
    };
    chart.setOption(option);
    chart.resize();
}

async function loadCostCapacityData(tech) {
    currentTech = tech;
    const url = `/explorer/cost_capacity_chart/?type=${encodeURIComponent(tech)}&region=${encodeURIComponent(currentRegion)}`;
    try {
        const response = await fetch(url, { method: 'GET', headers: { "Accept": "application/json" } });
        if (!response.ok) throw new Error("Network error: " + response.status);
        const data = await response.json();
        loadCostCapacityLineChart(data.line_data);
        const xValues = data.line_data.map(item => item[0]);
        if (xValues.includes(0)) {
            updateTechComparisonChart(0, tech);
        } else if (xValues.length > 0) {
            updateTechComparisonChart(xValues[0], tech);
        }
    } catch (error) {
        console.error("Error loading cost capacity data:", error);
    }
}

async function loadDemandData(scenario) {
    const url = `/explorer/demand_chart/?scenario_id=${encodeURIComponent(scenario)}&region=${encodeURIComponent(currentRegion)}`;
    try {
        const response = await fetch(url, { method: 'GET', headers: { "Accept": "application/json" } });
        if (!response.ok) throw new Error("Network error: " + response.status);
        const data = await response.json();
        loadDemandChart(data);
    } catch (error) {
        console.error("Error loading demand data:", error);
    }
}

function loadDemandCapacityData(scenario_id) {
    fetch(`/explorer/demand_capacity_chart/?scenario_id=${encodeURIComponent(scenario_id)}&region=${encodeURIComponent(currentRegion)}`, {
        method: 'GET',
        headers: { "Accept": "application/json" }
    })
    .then(response => {
        if (!response.ok) throw new Error("Network error: " + response.status);
        return response.json();
    })
    .then(data => {
        loadTechComparisonChart(data, scenario_id, "demand");
    })
    .catch(error => {
        console.error("Error updating the tech comparison chart:", error);
    });
}

function transformLineData(lineData) {
    const xValues = lineData.map(item => item[0]);
    const yValues = lineData.map(item => item[1]);
    const defaultIndex = xValues.includes(0) ? xValues.indexOf(0) : 0;
    const highlightColor = "#FF0000";
    const seriesData = yValues.map((val, index) =>
        index === defaultIndex ? { value: val, itemStyle: { color: highlightColor } } : { value: val }
    );
    return { xValues, yValues, seriesData };
}

function registerAxisPointerListener(chart, lastDataIndexRef) {
    chart.on('updateAxisPointer', function (event) {
        if (event.axesInfo && event.axesInfo.length > 0) {
            lastDataIndexRef.value = event.axesInfo[0].value;
        }
    });
}

function registerGlobalChartClick(chart, xValues, yValues, lastDataIndexRef) {
    chart.getZr().off('click');
    chart.getZr().on('click', function () {
        if (lastDataIndexRef.value == null) return;
        const highlightColor = "#FF0000";
        const newSeriesData = yValues.map((value, index) =>
            index === lastDataIndexRef.value ? { value: value, itemStyle: { color: highlightColor } } : value
        );
        chart.setOption({ series: [{ data: newSeriesData }] });
        const selectedX = xValues[lastDataIndexRef.value];
        updateTechComparisonChart(selectedX, currentTech);
    });
}

function loadCostCapacityLineChart(lineData) {
    const techCompChart = document.getElementById("tech-comparison-chart");
    const el = document.getElementById("cost-capacity-chart");
    if (!el) return;
    if (!lineData || lineData.length === 0) {
        removeChart(el);
        el.style.display = "relative";
        showErrorMessage(el, "Keine Daten verfügbar");
        if (techCompChart) techCompChart.style.display = "none";
        return;
    } else {
        removeErrorMessage(el);
        el.style.display = "block";
        techCompChart.style.display = "block";
    }
    const { xValues, yValues, seriesData } = transformLineData(lineData);
    const chart = getOrCreateChart(el);
    const option = {
        title: { text: "Kosten vs. installierte Leistung", left: "center" },
        tooltip: {
            trigger: "axis",
            formatter: (params) => {
                let idx = params[0].dataIndex;
                return `Kosten: ${xValues[idx]} €<br/>Leistung: ${yValues[idx]} MW`;
            }
        },
        grid: { left: '10%', right: '20%', top: '25%', bottom: '15%', containLabel: true },
        xAxis: { type: "category", name: "Kosten (€/MW)", data: xValues, axisPointer: { snap: true } },
        yAxis: { type: "value", name: "Installierte Leistung (MW)" },
        series: [{ type: "line", data: seriesData, smooth: true, showAllSymbol: true, symbol: "circle", symbolSize: 8 }]
    };
    chart.setOption(option);
    chart.resize();
    let lastDataIndexRef = { value: null };
    registerAxisPointerListener(chart, lastDataIndexRef);
    registerGlobalChartClick(chart, xValues, yValues, lastDataIndexRef);
}

function updateTechComparisonChart(selectedX, tech) {
    fetch(`/explorer/cost_capacity_chart/?type=${encodeURIComponent(tech)}&x=${encodeURIComponent(selectedX)}&region=${encodeURIComponent(currentRegion)}`, {
        method: 'GET',
        headers: { "Accept": "application/json" }
    })
    .then(response => {
        if (!response.ok) throw new Error("Network error: " + response.status);
        return response.json();
    })
    .then(data => {
        loadTechComparisonChart(data, selectedX);
    })
    .catch(error => {
        console.error("Error updating the tech comparison chart:", error);
    });
}

function loadTechComparisonChart(data, selectedX, category="cost") {
    const div_id = category === "cost" ? "tech-comparison-chart" : "demand-tech-comparison-chart";
    let el = document.getElementById(div_id);
    if (!el) return;
    let chart = getOrCreateChart(el);
    let barData = data.bar_data || [];
    if (barData.length === 0) {
         removeChart(el);
         showErrorMessage(el, "Das Modell hat unter den getroffenen Annahmen keinen Ausbau der ausgewählten Technologie vorgesehen.");
         return;
    } else {
        removeErrorMessage(el);
        el.style.display = "block";
    }
    let categories = barData.map(item => item.name);
    let values = barData.map(item => ({ value: item.value, itemStyle: { color: item.color } }));

    let storedZoomStart = chartZoomStart[category];
    let storedZoomEnd = chartZoomEnd[category];

    let option = {
        title: { text: category === "cost" ? `Technologievergleich bei Kosten von ${selectedX} €` : `Technologievergleich für Szenario ${selectedX}`, left: "center" },
        tooltip: { trigger: "item", formatter: (params) => `${params.name}<br/>Wert: ${params.value}` },
        grid: { left: '10%', right: '20%', top: '25%', bottom: '15%', containLabel: true },
        xAxis: { type: "value", name: "Leistung" },
        yAxis: { type: "category", data: categories },
        dataZoom: [
            {
                type: 'slider',
                show: true,
                orient: 'horizontal',
                start: storedZoomStart !== null ? parseFloat(storedZoomStart) : 0,
                end: storedZoomEnd !== null ? parseFloat(storedZoomEnd) : 100
            }
        ],
        series: [{ type: "bar", data: values }]
    };
    chart.setOption(option);
    chart.resize();

    chart.on('datazoom', function(params) {
        const zoomState = chart.getOption().dataZoom[0];
        chartZoomStart[category] = zoomState.start;
        chartZoomEnd[category] = zoomState.end;
    });
}

function showErrorMessage(el, message) {
    let errorMsg = el.querySelector('.error-message');
    if (!errorMsg) {
        errorMsg = document.createElement('div');
        errorMsg.className = 'error-message';
        errorMsg.style.position = "absolute";
        errorMsg.style.top = "10px";
        errorMsg.style.left = "0";
        errorMsg.style.width = "100%";
        errorMsg.style.textAlign = 'center';
        errorMsg.style.padding = '20px';
        el.appendChild(errorMsg);
    }
    errorMsg.textContent = message;
}

function removeErrorMessage(el) {
    let errorMsg = el.querySelector('.error-message');
    if (errorMsg) {
        errorMsg.parentNode.removeChild(errorMsg);
    }
}


function initializeTechnologySelect() {
    const dropdown = document.getElementById("technologySelect");
    if (dropdown && dropdown.options.length > 0) {
        const firstOptionValue = dropdown.options[0].value;
        loadCostCapacityData(firstOptionValue);
    }
}

function loadRanges() {
    loadRangesData(1, 'ranges-chart-1', 'ranges-table-1');
    loadRangesData(2, 'ranges-chart-2', 'ranges-table-2');
  }

/**
 * Fetch data from /ranges endpoint and build the chart + table.
 * @param {string} region
 * @param {number} divergence
 * @param {string} chartId
 * @param {string} tableId
 */
function loadRangesData(divergence, chartId, tableId) {
  const url = `/explorer/ranges/?region=${encodeURIComponent(currentRegion)}&divergence=${divergence}`;

  fetch(url)
    .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status} ${response.statusText}`);
    }
    return response.json();
    })
    .then(jsonData => {
      // jsonData = { region, divergence, ranges: {...} }
      const rangesDict = jsonData.ranges;

      // Convert the dictionary to a list for eCharts
      const chartData = buildChartData(rangesDict);
      renderChart(chartId, chartData);

      // Build table rows
      const tableRows = buildTableRows(rangesDict);
      renderTable(tableId, tableRows);
      syncRowHeight(chartId, tableId, chartData.length);
      window.addEventListener('resize', () => {
        syncRowHeight(chartId, tableId, chartData.length);
      });
      document.querySelectorAll(".alternative").forEach((element, i) => {
        element.addEventListener("click", () => syncRowHeight(chartId, tableId, chartData.length));
      });
    })
    .catch(err => console.error("Error fetching ranges data:", err));
}

/**
 * Build data for eCharts from the server dictionary
 * e.g. transforms { "boiler_large": {...}, "boiler_small": {...} } into an array
 */
function buildChartData(rangesDict) {
  // We'll return an array of objects with: { technology, minCap, maxCap, diff, color }
  const dataArray = [];

  for (const [tech, vals] of Object.entries(rangesDict)) {
    const minCap = vals.min_capacity || 0;
    const maxCap = vals.max_capacity || 0;
    const diff = Math.max(maxCap - minCap, 0);
    const color = vals.color || "#3B82F6";  // or client-side fallback
    dataArray.push({
      technology: tech,
      name: vals.tech_name || "",
      minCap,
      maxCap,
      diff,
      color,
      potential: vals.potential || null,
      potentialUnit: vals.potential_unit || "",
      minCost: vals.min_cost || 0,
      maxCost: vals.max_cost || 0
    });
  }

  return dataArray;
}

/**
 * Render the horizontal range chart with stacked bars
 */
function renderChart(chartId, dataArray) {
  const chartDom = document.getElementById(chartId);
  if (!chartDom) return;
  const myChart = echarts.init(chartDom);

  // Build arrays for the 'offset' (minCap) and 'range' (diff)
  const offsetData = dataArray.map(item => item.minCap);
  const rangeData = dataArray.map(item => item.diff);
  const colorList = dataArray.map(item => item.color);

  // We also need the yAxis categories = technology
  const yCategories = dataArray.map(item => item.name);

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: function (params) {
        // params is an array (since it's stacked)
        // We only really want to show min-max
        const rangeItem = params.find(p => p.seriesName === 'Capacity Range');
        if (!rangeItem) return '';
        const idx = rangeItem.dataIndex;
        const item = dataArray[idx];
        return `
          <div>
            <strong>${item.name}</strong><br/>
            min: ${item.minCap.toFixed(0)} – max: ${item.maxCap.toFixed(0)}
          </div>
        `;
      }
    },
    grid: {
      top: 45,      // Must equal table header row height
      bottom: '-1.64%',    // Must be non-zero, as otherwise last y-category tick is not drawn
      containLabel: true,
    },
    xAxis: {
      type: 'value',
      name: 'Capacity',
      show : false,
      axisTick: { show: false }
    },
    yAxis: {
      type: 'category',
      data: yCategories,
      inverse: true,
      axisTick: { show: true },
      show : true,
      containLabel: true,
    },
    series: [
      // 1) Offset series (transparent)
      {
        name: 'Offset',
        type: 'bar',
        stack: 'Total',
        data: offsetData,
        itemStyle: { color: 'transparent' }
      },
      // 2) Range series (colored)
      {
        name: 'Capacity Range',
        type: 'bar',
        stack: 'Total',
        data: rangeData.map((val, idx) => {
          return {
            value: val,
            itemStyle: {
              color: colorList[idx]
            }
          };
        }),
        barWidth: 30
      }
    ]
  };

  myChart.setOption(option);
}

/**
 * Build the rows for the table
 */
function buildTableRows(rangesDict) {
  // For each technology, build an object with the 4 columns:
  // "Technologie", "Leistung/Kapazität", "Technisches Potential", "Kosten"
  const rows = [];

  for (const [tech, vals] of Object.entries(rangesDict)) {
    const tech_name = vals.tech_name;
    const capStr = vals.cap_str || "";
    const costStr = vals.cost_str || "";
    const potStr = vals.pot_str || "";

    rows.push({
      technology: tech_name,
      capacity: capStr,
      potential: potStr,
      cost: costStr
    });
  }

  return rows;
}

/**
 * Render the table
 */
function renderTable(tableId, rows) {
  const tableElem = (document.querySelector(`#${tableId}`));
  const tbody = tableElem.querySelector("tbody");
  if (tbody !== null) {
      tbody.remove();
  }
  const tableBody = document.createElement('tbody');
  tableElem.appendChild(tableBody);

  // Clear old rows
  tableBody.innerHTML = '';

  rows.forEach(row => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${row.capacity}</td>
      <td>${row.potential}</td>
      <td>${row.cost}</td>
    `;
    tableBody.appendChild(tr);
  });
}

function syncRowHeight(chartId, tableId, dataLength) {
  const chartElem = document.getElementById(chartId);
  // console.log("started syncRowHeight");
  if (!chartElem) return;

  echarts.getInstanceByDom(chartElem).resize();

  // The total height of the chart container
  const chartHeight = chartElem.clientHeight;

  // console.log("clientHeight: " + chartHeight);

  // Subtract table header height = chart.grid.top + chart.grid.bottom
  const rowHeight = (chartHeight - 31) / dataLength;

  // Select all <tr> within the table
  const rows = document.querySelectorAll(`#${tableId} tbody tr`);
  rows.forEach(row => {
    row.style.height = rowHeight + 'px';
    // console.log("roeHeight: " + rowHeight);
  });
  // console.log("ended syncRowHeight");
}

function showDropdownBasicSolution(region){
    const dropdown = document.getElementById('region-select');
  if (!dropdown) return;

  if (region === 'einzeln') {
    dropdown.style.display = 'inline-block';
  } else {
    dropdown.style.display = 'none';
  }
}

document.addEventListener("DOMContentLoaded", () => {
    const dropdown = document.getElementById("region-select");
    if (dropdown) {
        dropdown.addEventListener("change", function () {
            const selectedregion = this.value;
            loadBasicData(selectedregion);
        });
    }
});

// Update the sticky header with the region's title and image
function updateStickyHeader(title) {
  const titleEl = document.getElementById('sticky-region-title');
  titleEl.textContent = title;
}

document.addEventListener('DOMContentLoaded', () => {
  // 1) Determine navbar height to offset the sticky header
  const navbar    = document.querySelector('.navbar__wrap');
  const navHeight = navbar ? navbar.offsetHeight : 0;

  // Apply that offset so sticky-header sits just below main nav
  const stickyHeader = document.getElementById('sticky-region-header');
  stickyHeader.style.top = `${navHeight}px`;

  // 2) Bind click events to all select-buttons
  document.querySelectorAll('.select-button').forEach(button => {
    button.addEventListener('click', event => {
      const wrapper = event.currentTarget.closest('.results__region-container');
      const title   = wrapper.dataset.regionName;

      // 2a) Update the sticky header
      updateStickyHeader(title);
    });
  });

  // 3) Show/hide the sticky header when the first card scrolls out of view
 const firstTitle = document.querySelector(
    '.results__region-container[data-region-name] .results__top-row h2'
  );
  if (firstTitle) {
    new IntersectionObserver(
      ([entry]) => {
        stickyHeader.classList.toggle('visible', !entry.isIntersecting);
      },
      {
        root: null,
        rootMargin: `-${navHeight}px 0px 0px 0px`,
        threshold: 0
      }
    ).observe(firstTitle);
  }
});

function loadDemandChart(data) {
  let el = document.getElementById("demand-chart");
  if (!el) return;
  let chart = getOrCreateChart(el);
  // 1) grid definitions
  const grid = [];
  for (let r = 0; r < 4; r++) {
    grid.push({
      top: `${r * 25}%`,
      height: '25%'
    });
  }

  // 2) xAxis / yAxis
  const xAxis = Array.from({ length: 4 }, (_, idx) => {
     return {
      gridIndex: idx,
      type: 'category',
      axisTick: { show: false },
      axisLabel: { margin: 10 },
      axisLine: {
        onZero: false,
        lineStyle: { color: '#000', width: 1 }
      }
    };
  });

  const yAxis = Array.from({ length: 8 }, (_, idx) => ({
    gridIndex: Math.floor(idx / 2),
    type: 'value',
    axisLabel: { show: false },
    axisLine:  { show: false },
    splitLine:{ show: false }
  }));

  // 3) series mapping
  const mapping = {
    0:  'electricity-demand_hh',
    1:  'heat_low_central-demand_hh',
    2:  'heat_low_decentral-demand_hh',
    3:  '',
    4:  'electricity-demand_mob',
    5:  '',
    6:  '',
    7:  '',
    8:  'electricity-demand_cts',
    9:  'heat_low_central-demand_cts',
    10: 'heat_low_decentral-demand_cts',
    11:  '',
    12: 'electricity-demand_ind',
    13: 'heat_low_central-demand_ind',
    14: 'heat_low_decentral-demand_ind',
    15: 'heat_high-demand_ind'
  };

  function mapYAxis(idx) {
    if (idx % 4 === 0) return idx / 2;
    return Math.floor(idx / 4) * 2 + 1;
  }

  const series = Object.entries(mapping)
    .map(([idx, key]) => {
      const entry = data[key];
      if (!entry || entry.demand == null) return {
        type: 'bar',
        stack: idx,
        xAxisIndex: Math.floor(idx / 4),
        yAxisIndex: mapYAxis(idx),
        data: [ null ],
        barWidth: '15%',
      };
      return {
        name: key,
        type: 'bar',
        stack: idx,
        xAxisIndex: Math.floor(idx / 4),
        yAxisIndex: mapYAxis(idx),
        data: [ entry.diff < 0 ? entry.demand + entry.diff : entry.demand ],
        barWidth: '15%',
        itemStyle: { color: entry.color}
      };
    });

  const seriesDiffs = Object.entries(mapping)
    .map(([idx, key]) => {
      const entry = data[key];
      if (!entry || entry.demand == null) return {
        type: 'bar',
        stack: idx,
        xAxisIndex: Math.floor(idx / 4),
        yAxisIndex: mapYAxis(idx),
        data: [ null ],
        barWidth: '15%',
      };
      return {
        name: key,
        type: 'bar',
        stack: idx,
        xAxisIndex: Math.floor(idx / 4),
        yAxisIndex: mapYAxis(idx),
        data: [ Math.abs(entry.diff) ],
        barWidth: '15%',
        itemStyle: { color: adjust_color(entry.color, entry.diff < 0 ? -20 : 20) }
      };
    });

  // 4) static graphics
  const graphic = [
    { type: 'text', left: '5%',  top: '0%',   style: { text: 'Strom', textAlign: 'center', font: '16px Arial' } },
    { type: 'text', left: '59%', top: '0%',   style: { text: 'Wärme', textAlign: 'center', font: '16px Arial' } },
    { type: 'text', right:'2%', top: '11.5%', style: { text: 'Haushalte', textAlign: 'right', font: '14px Arial' } },
    { type: 'text', right:'2%', top: '36.5%', style: { text: 'Verkehr',   textAlign: 'right', font: '14px Arial' } },
    { type: 'text', right:'2%', top: '61.5%', style: { text: 'GHD',       textAlign: 'right', font: '14px Arial' } },
    { type: 'text', right:'2%', top: '86.5%', style: { text: 'Industrie', textAlign: 'right', font: '14px Arial' } }
  ];

  // 5) assemble & render
  const option = {
    grid,
    xAxis,
    yAxis,
    series: series.concat(seriesDiffs),
    graphic,
    tooltip: { trigger: 'item' },
    legend: { show: false }
  };

  chart.setOption(option);
  chart.resize();
}

function adjust_color(color, amount) {
  // From https://stackoverflow.com/a/57401891/5804947
  return '#' + color.replace(/^#/, '').replace(/../g, color => ('0'+Math.min(255, Math.max(0, parseInt(color, 16) + amount)).toString(16)).substr(-2));
}
