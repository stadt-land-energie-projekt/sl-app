function getOrCreateChart(domElement) {
    let chart = echarts.getInstanceByDom(domElement);
    if (chart) {
        chart.clear();
    } else {
        chart = echarts.init(domElement, null, { renderer: "svg" });
    }
    return chart;
}

function loadFlowsChart(chartType) {
    let url = window.location.origin + "/explorer/chart/flow_chart?type=" + encodeURIComponent(chartType);

    fetch(url, {
        method: "GET",
        mode: "cors",
        headers: { "Accept": "application/json" },
        credentials: "same-origin"
    })
    .then(response => response.json())
    .then(jsonObj => {
        let dataArray = jsonObj.data;

        if (!Array.isArray(dataArray) || dataArray.length < 2) {
            console.error("Unerwartetes Datenformat:", dataArray);
            return;
        }

        let electricityData = dataArray[0];
        createFlowChart(
            document.getElementById("electricity-chart"),
            electricityData,
            "electricity"
        );

        let hydrogenData = dataArray[1];
        createFlowChart(
            document.getElementById("hydrogen-chart"),
            hydrogenData,
            "hydrogen"
        );
    })
    .catch(error => {
        console.error("Error loading flow chart:", error);
    });
}

function createFlowChart(domElement, chartData, resource) {
    if (!domElement || !chartData) return;

    let chart = getOrCreateChart(domElement);

    let values = chartData.energyData.map(d => d.value);
    let minEnergy = Math.min(...values);
    let maxEnergy = Math.max(...values);

    function scaleLineWidth(value) {
        let diff = maxEnergy - minEnergy;
        if (diff === 0) {
            return 4;
        }
        return 1 + ((value - minEnergy) / diff) * 7;
    }

    let gradientColors = [
      { offset: 0, color: "#a2edbd" },
      { offset: 1, color: "#20a54f" }
    ];

    if (resource === "hydrogen") {
      gradientColors = [
        { offset: 0, color: "#feb1b1" },
        { offset: 1, color: "#c34747" }
      ];
    }

    let option = {
        title: {
            text: chartData.title || "Flussdiagramm",
            left: "center"
        },
        tooltip: {
            trigger: "item",
            formatter: function (params) {
                if (params.dataType === "edge") {
                    return `${params.data.source} → ${params.data.target}: ${params.data.value} MWh`;
                }
                return params.name;
            }
        },
        series: [{
            type: "graph",
            layout: "force",
            force: {
                repulsion: 300,
                edgeLength: [50, 200]
            },
            roam: true,
            zoom: 0.2,
            label: {
                show: true,
                position: "right",
                fontSize: 20
            },
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
                lineStyle: {
                    width: scaleLineWidth(d.value)
                }
            })),
            emphasis: {
                focus: "adjacency"
            }
        }]
    };

    chart.setOption(option);
    chart.resize();
}


function showHiddenDiv(chartType, button) {
    let allButtons = document.querySelectorAll(".select-button");
    allButtons.forEach(b => b.classList.remove("selected"));

    button.classList.add("selected");

    let hiddenDiv = document.querySelector(".hidden-div");
    hiddenDiv.style.display = "block";

    loadFlowsChart(chartType, "electricity");
    loadFlowsChart(chartType, "hydrogen");
    }

function loadElectricityChart(data) {
    let el = document.getElementById("chart-electricity");
    if (!el) return;

    let chart = getOrCreateChart(el);

    // Data from the context dictionary
    let categories = data.categories || [];
    let seriesData = data.series || {};

    // Convert our "series" dict into ECharts series array
    let series = [];
    Object.keys(seriesData).forEach((key) => {
        series.push({
            name: key,
            type: "bar",
            stack: "electricityStack",
            data: seriesData[key]
        });
    });

    let option = {
        title: { text: "Electricity (GWh)", left: "center" },
        tooltip: { trigger: "axis" },
        legend: { top: 30 },
        grid: { left: "10%", right: "10%", bottom: "10%" },
        xAxis: { type: "value" },
        yAxis: {
            type: "category",
            data: categories
        },
        series: series
    };

    chart.setOption(option);
    chart.resize();
}

/**
 * Load Heat chart (horizontal stacked bar).
 */
function loadHeatChart(data) {
    let el = document.getElementById("chart-heat");
    if (!el) return;

    let chart = getOrCreateChart(el);

    let categories = data.categories || [];
    let seriesData = data.series || {};

    let series = [];
    Object.keys(seriesData).forEach((key) => {
        series.push({
            name: key,
            type: "bar",
            stack: "heatStack",
            data: seriesData[key]
        });
    });

    let option = {
        title: { text: "Heat (GWh)", left: "center" },
        tooltip: { trigger: "axis" },
        legend: { top: 30 },
        grid: { left: "10%", right: "10%", bottom: "10%" },
        xAxis: { type: "value" },
        yAxis: {
            type: "category",
            data: categories
        },
        series: series
    };

    chart.setOption(option);
    chart.resize();
}

/**
 * Load Capacity chart (horizontal stacked bar).
 */
function loadCapacityChart(data) {
    let el = document.getElementById("chart-capacity");
    if (!el) return;

    let chart = getOrCreateChart(el);

    let categories = data.categories || [];
    let seriesData = data.series || {};

    let series = [];
    Object.keys(seriesData).forEach((key) => {
        series.push({
            name: key,
            type: "bar",
            stack: "capacityStack",
            data: seriesData[key]
        });
    });

    let option = {
        title: { text: "Capacity (MW)", left: "center" },
        tooltip: { trigger: "axis" },
        legend: { top: 30 },
        grid: { left: "10%", right: "10%", bottom: "10%" },
        xAxis: { type: "value" },
        yAxis: {
            type: "category",
            data: categories
        },
        series: series
    };

    chart.setOption(option);
    chart.resize();
}

/**
 * Load Costs chart (horizontal stacked bar).
 */
function loadCostsChart(data) {
    let el = document.getElementById("chart-costs");
    if (!el) return;

    let chart = getOrCreateChart(el);

    let categories = data.categories || [];
    let seriesData = data.series || {};

    let series = [];
    Object.keys(seriesData).forEach((key) => {
        series.push({
            name: key,
            type: "bar",
            stack: "costsStack",
            data: seriesData[key]
        });
    });

    let option = {
        title: { text: "Costs (€)", left: "center" },
        tooltip: { trigger: "axis" },
        legend: { top: 30 },
        grid: { left: "10%", right: "10%", bottom: "10%" },
        xAxis: { type: "value" },
        yAxis: {
            type: "category",
            data: categories
        },
        series: series
    };

    chart.setOption(option);
    chart.resize();
}

document.addEventListener("DOMContentLoaded", function() {
    loadElectricityChart(electricityChartData);
    loadHeatChart(heatChartData);
    loadCapacityChart(capacityChartData);
    loadCostsChart(costsChartData);
});
