let currentRegion = "";
let currentTech = "";

// Called when a region button is clicked
async function showHiddenDiv(region, button) {
    let allButtons = document.querySelectorAll(".select-button");
    allButtons.forEach(b => b.classList.remove("selected"));

    button.classList.add("selected");

    let hiddenDiv = document.querySelector(".hidden-div");
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

async function loadBasicData(region) {
    const url = `/explorer/basic_charts/?type=${encodeURIComponent(region)}`;
    try {
        const response = await fetch(url, { method: 'GET', headers: { "Accept": "application/json" } });
        if (!response.ok) throw new Error("Netzwerkfehler: " + response.status);
        const data = await response.json();
        loadElectricityChart(data.electricity);
        loadHeatChart(data.heat);
        loadCapacityChart(data.capacity);
        loadCostsChart(data.costs);
    } catch (error) {
        console.error("Fehler beim Laden der Basisdaten:", error);
    }
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

function loadElectricityChart(data) {
    let el = document.getElementById("basic-electricity");
    if (!el) return;
    let chart = getOrCreateChart(el);
    let categories = data.categories || [];
    let seriesData = data.series || {};
    let series = Object.keys(seriesData).map(key => ({
        name: key,
        type: "bar",
        stack: "electricityStack",
        data: seriesData[key]
    }));
    let option = {
        title: { text: "Elektrizität (GWh)", left: "center" },
        tooltip: { trigger: "axis" },
        legend: { top: 30 },
        grid: { left: "10%", right: "10%", bottom: "10%" },
        xAxis: { type: "value" },
        yAxis: { type: "category", data: categories },
        series: series
    };
    chart.setOption(option);
    chart.resize();
}

function loadHeatChart(data) {
    let el = document.getElementById("basic-heat");
    if (!el) return;
    let chart = getOrCreateChart(el);
    let categories = data.categories || [];
    let seriesData = data.series || {};
    let series = Object.keys(seriesData).map(key => ({
        name: key,
        type: "bar",
        stack: "heatStack",
        data: seriesData[key]
    }));
    let option = {
        title: { text: "Wärme (GWh)", left: "center" },
        tooltip: { trigger: "axis" },
        legend: { top: 30 },
        grid: { left: "10%", right: "10%", bottom: "10%" },
        xAxis: { type: "value" },
        yAxis: { type: "category", data: categories },
        series: series
    };
    chart.setOption(option);
    chart.resize();
}

function loadCapacityChart(data) {
    let el = document.getElementById("basic-capacity");
    if (!el) return;
    let chart = getOrCreateChart(el);
    let categories = data.categories || [];
    let seriesData = data.series || {};
    let series = Object.keys(seriesData).map(key => ({
        name: key,
        type: "bar",
        stack: "capacityStack",
        data: seriesData[key]
    }));
    let option = {
        title: { text: "Kapazität (MW)", left: "center" },
        tooltip: { trigger: "axis" },
        legend: { top: 30 },
        grid: { left: "10%", right: "10%", bottom: "10%" },
        xAxis: { type: "value" },
        yAxis: { type: "category", data: categories },
        series: series
    };
    chart.setOption(option);
    chart.resize();
}

function loadCostsChart(data) {
    let el = document.getElementById("basic-costs");
    if (!el) return;
    let chart = getOrCreateChart(el);
    let categories = data.categories || [];
    let seriesData = data.series || {};
    let series = Object.keys(seriesData).map(key => ({
        name: key,
        type: "bar",
        stack: "costsStack",
        data: seriesData[key]
    }));
    let option = {
        title: { text: "Kosten (€)", left: "center" },
        tooltip: { trigger: "axis" },
        legend: { top: 30 },
        grid: { left: "10%", right: "10%", bottom: "10%" },
        xAxis: { type: "value" },
        yAxis: { type: "category", data: categories },
        series: series
    };
    chart.setOption(option);
    chart.resize();
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
        xAxis: { type: "category", name: "Kosten (€)", data: xValues, axisPointer: { snap: true } },
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
         showErrorMessage(el, "Keine Daten verfügbar");
         return;
    } else {
        removeErrorMessage(el);
        el.style.display = "block";
    }
    let categories = barData.map(item => item.name);
    let values = barData.map(item => ({ value: item.value, itemStyle: { color: item.color } }));
    let option = {
        title: { text: "Technologievergleich bei Kosten von " + selectedX + " €", left: "center" },
        tooltip: { trigger: "item", formatter: (params) => `${params.name}<br/>Wert: ${params.value}` },
        grid: { left: '10%', right: '20%', top: '25%', bottom: '15%', containLabel: true },
        xAxis: { type: "value", name: "Leistung" },
        yAxis: { type: "category", data: categories },
        series: [{ type: "bar", data: values }]
    };
    chart.setOption(option);
    chart.resize();
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
