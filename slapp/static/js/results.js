let currentRegion = "";

function showHiddenDiv(region, button) {
    let allButtons = document.querySelectorAll(".select-button");
    allButtons.forEach(b => b.classList.remove("selected"));

    button.classList.add("selected");

    let hiddenDiv = document.querySelector(".hidden-div");
    hiddenDiv.style.display = "block";

    loadFlowsChart(region, "electricity");
    loadFlowsChart(region, "hydrogen");
    loadBasicData(region);
    currentRegion = region;
    }

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
            force: {
                repulsion: 300,
                edgeLength: [50, 200]
            },
            roam: true,
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

function loadElectricityChart(data) {
    let el = document.getElementById("basic-electricity");
    if (!el) return;

    let chart = getOrCreateChart(el);

    let categories = data.categories || [];
    let seriesData = data.series || {};

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

function loadHeatChart(data) {
    let el = document.getElementById("basic-heat");
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

function loadCapacityChart(data) {
    let el = document.getElementById("basic-capacity");
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

function loadCostsChart(data) {
    let el = document.getElementById("basic-costs");
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

function loadBasicData(region) {
    fetch(`/explorer/basic_charts/?type=${encodeURIComponent(region)}`, {
        method: 'GET',
        headers: {
            "Accept": "application/json",
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Netzwerkfehler: " + response.status);
        }
        return response.json();
    })
    .then(data => {
        loadElectricityChart(data.electricity);
        loadHeatChart(data.heat);
        loadCapacityChart(data.capacity);
        loadCostsChart(data.costs);
    })
    .catch(error => {
        console.error("Fehler beim Laden der Basislösung-Daten:", error);
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

let currentTech = "";

function getNearestIndex(chart, xValues, params) {
    const clickX = params.event.offsetX;
    const clickY = params.event.offsetY;

    const [dataX] = chart.convertFromPixel({ seriesIndex: 0 }, [clickX, clickY]);

    let minDist = Infinity;
    let nearestIdx = -1;
    xValues.forEach((val, i) => {
        const dist = Math.abs(val - dataX);
        if (dist < minDist) {
            minDist = dist;
            nearestIdx = i;
        }
    });

    return nearestIdx;
}

function loadCostCapacityData(tech) {
    currentTech = tech;
    fetch(`/explorer/cost_capacity_chart/?type=${encodeURIComponent(tech)}&region=${encodeURIComponent(currentRegion)}`, {
        method: 'GET',
        headers: { "Accept": "application/json" }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network error: " + response.status);
        }
        return response.json();
    })
    .then(data => {
        loadCostCapacityLineChart(data.line_data);
        let xValues = data.line_data.map(data => data[0]);
        if (xValues.includes(0)) {
            updateTechComparisonChart(0, tech);
        } else if (xValues.length > 0) {
            updateTechComparisonChart(xValues[0], tech);
        }
    })
    .catch(error => {
        console.error("Error loading cost capacity data:", error);
    });
}

function loadCostCapacityLineChart(lineData) {
    let techCompChart = document.getElementById("tech-comparison-chart");
    let el = document.getElementById("cost-capacity-chart");
    if (!el) return;

    if (!lineData || lineData.length === 0) {
        removeChart(el);
        el.style.display = "relative";
        showErrorMessage(el, "Keine Daten verfügbar");
        if (techCompChart) {
            techCompChart.style.display = "none";
        }
        return;
    } else {
        removeErrorMessage(el);
        el.style.display = "block";
        techCompChart.style.display = "block";
    }

    let xValues = lineData.map(data => data[0]);
    let yValues = lineData.map(data => data[1]);

    let chart = getOrCreateChart(el);

    let defaultIndex = (xValues.includes(0)) ? xValues.indexOf(0) : 0;
    let seriesData = yValues.map((val, index) => {
        if (index === defaultIndex) {
            return { value: val, itemStyle: { color: "#FF0000" } };
        }
        return { value: val };
    });

    let option = {
        title: {
            text: "Kosten vs. Installierte Leistung",
            left: "center"
        },
        tooltip: {
            trigger: "axis",
            formatter: (params) => {
                let idx = params[0].dataIndex;
                let xVal = xValues[idx];
                let yVal = yValues[idx];
                return `Kosten: ${xVal} €<br/>Leistung: ${yVal} MW`;
            }
        },
        grid: {
          left: '10%',
          right: '20%',
          top: '25%',
          bottom: '15%',
          containLabel: true
        },
        xAxis: {
            type: "category",
            name: "Kosten (€)",
            data: xValues
        },
        yAxis: {
            type: "value",
            name: "Installierte Leistung (MW)"
        },
        series: [
            {
                type: "line",
                data: seriesData,
                smooth: true,
                symbol: "circle",
                symbolSize: 8,
            }
        ]
    };
    chart.setOption(option);
    chart.resize();

   chart.off('click');
    chart.on('click', function (e) {
        let idx = e.dataIndex;
        if (idx === undefined || idx < 0 || idx >= xValues.length) {
            return;
        }
        const highlightColor = "#FF0000";
        let newSeriesData = yValues.map((value, index) => {
            if (index === idx) {
                return { value: value, itemStyle: { color: highlightColor } };
            } else {
                return value;
            }
        });
        chart.setOption({
            series: [{
                data: newSeriesData
            }]
        });
        let selectedX = xValues[idx];
        updateTechComparisonChart(selectedX, currentTech);
    });
}

function updateTechComparisonChart(selectedX, tech) {
    fetch(`/explorer/cost_capacity_chart/?type=${encodeURIComponent(tech)}&x=${encodeURIComponent(selectedX)}&region=${encodeURIComponent(currentRegion)}`, {
        method: 'GET',
        headers: { "Accept": "application/json" }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network error: " + response.status);
        }
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
    }else {
    removeErrorMessage(el);
    el.style.display = "block";
    }

    let categories = barData.map(item => item.name);
    let values = barData.map(item => ({
        value: item.value,
        itemStyle: { color: item.color }
    }));

    let option = {
        title: {
            text: "Technologievergleich bei Kosten von " + selectedX + " €",
            left: "center"
        },
        tooltip: {
            trigger: "item",
            formatter: (params) => `${params.name}<br/>Value: ${params.value}`
        },
         grid: {
            left: '10%',
            right: '20%',
            top: '25%',
            bottom: '15%',
            containLabel: true
          },
        xAxis: {
            type: "value",
            name: "Leistung"
        },
        yAxis: {
            type: "category",
            data: categories
        },
        series: [
            {
                type: "bar",
                data: values
            }
        ]
    };

    chart.setOption(option);
    chart.resize();
}

/**
 * Dropdown integration:
 * When a dropdown item is clicked, the selected technology type is retrieved and the charts are reloaded.
 */
document.querySelectorAll('option').forEach(item => {
    item.addEventListener('click', function(event) {
        const selectedType = this.getAttribute('value');

        loadCostCapacityData(selectedType);
        showTechData();
    });
});


function showTechData() {
    techContainer = document.getElementById("tech-container")
    if (techContainer) {
        techContainer.classList.remove("hide");
        techContainer.classList.add("active");
    }
}
