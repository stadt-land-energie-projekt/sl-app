let currentRegion = "";
let currentTech = "";

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
    const dropdown = document.getElementById("technologySelect");
    if (dropdown) {
        dropdown.addEventListener("change", function () {
            const selectedType = this.value;
            loadCostCapacityData(selectedType);
        });
        if (dropdown.options.length > 0) {
            currentTech = dropdown.options[0].value;
            loadCostCapacityData(currentTech);
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
        let dataArray = jsonObj.data;
        if (!Array.isArray(dataArray) || dataArray.length < 2) {
            console.error("Unerwartetes Datenformat:", dataArray);
            return;
        }
        createFlowChart(document.getElementById("electricity-chart"), dataArray[0], "electricity");
        createFlowChart(document.getElementById("hydrogen-chart"), dataArray[1], "hydrogen");
    } catch (error) {
        console.error("Error loading flow chart:", error);
    }
}

function createFlowChart(domElement, chartData, resource) {
    if (!domElement || !chartData) return;
    let chart = getOrCreateChart(domElement);
    let values = chartData.energyData.map(d => d.value);
    let minEnergy = Math.min(...values);
    let maxEnergy = Math.max(...values);
    function scaleLineWidth(value) {
        let diff = maxEnergy - minEnergy;
        return diff === 0 ? 4 : 1 + ((value - minEnergy) / diff) * 7;
    }
    let gradientColors = resource === "hydrogen" ?
        [{ offset: 0, color: "#feb1b1" }, { offset: 1, color: "#c34747" }] :
        [{ offset: 0, color: "#a2edbd" }, { offset: 1, color: "#20a54f" }];
    let option = {
        title: { text: chartData.title || "Flussdiagramm", left: "center" },
        tooltip: {
            trigger: "item",
            formatter: function (params) {
                return params.dataType === "edge" ?
                    `${params.data.source} → ${params.data.target}: ${params.data.value} MWh` : params.name;
            }
        },
        series: [{
            type: "graph",
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
            data: chartData.nodes,
            links: chartData.energyData.map(d => ({
                source: d.source,
                target: d.target,
                value: d.value,
                lineStyle: { width: scaleLineWidth(d.value) }
            })),
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

function loadTechComparisonChart(data, selectedX) {
    let el = document.getElementById("tech-comparison-chart");
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

    let storedZoomStart = localStorage.getItem('chartZoomStart');
    let storedZoomEnd = localStorage.getItem('chartZoomEnd');

    let option = {
        title: { text: "Technologievergleich bei Kosten von " + selectedX + " €", left: "center" },
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
        localStorage.setItem('chartZoomStart', zoomState.start);
        localStorage.setItem('chartZoomEnd', zoomState.end);
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
