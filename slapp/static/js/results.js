function showHiddenDiv(region, button) {
    let allButtons = document.querySelectorAll(".select-button");
    allButtons.forEach(b => b.classList.remove("selected"));

    button.classList.add("selected");

    let hiddenDiv = document.querySelector(".hidden-div");
    hiddenDiv.style.display = "block";

    loadFlowsChart(region, "electricity");
    loadFlowsChart(region, "hydrogen");
    loadBasicData(region);
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

function loadCostCapacityLineChart(data) {
    let el = document.getElementById("line-chart");
    if (!el) return;

    let chart = getOrCreateChart(el);

    let lineData = data.line_data || [];

    let option = {
        title: {
            text: "Kosten vs. Installierte Leistung",
            left: "center"
        },
        tooltip: {
            trigger: "axis",
            formatter: (params) => {
                let value = params[0].value;
                let xVal = value[0];
                let yVal = value[1];
                return `Kosten: ${xVal} €<br/>Leistung: ${yVal} MW`;
            }
        },
        xAxis: {
            type: "value",
            name: "Kosten (€)"
        },
        yAxis: {
            type: "value",
            name: "Installierte Leistung (MW)"
        },
        series: [
            {
                type: "line",
                data: lineData,
                smooth: true
            }
        ]
    };

    chart.setOption(option);
    chart.resize();
}

function loadHorizontalBarChart(data) {
    let el = document.getElementById("bar-chart");
    if (!el) return;

    let chart = getOrCreateChart(el);

    let barData = data.bar_data || [];

    let categories = barData.map(item => item.name);
    let values = barData.map(item => item.value);

    let option = {
        title: {
            text: "Horizontales Balkendiagramm",
            left: "center"
        },
        tooltip: {
            trigger: "item",
            formatter: (params) => {
                return `${params.name}<br/>Wert: ${params.value}`;
            }
        },
        xAxis: {
            type: "value",
            name: "Wert"
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

function loadCostCapacityData(type) {
    fetch(`/explorer/cost_capacity_chart/?type=${encodeURIComponent(type)}`, {
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
        loadCostCapacityLineChart(data);
        loadHorizontalBarChart(data);
    })
    .catch(error => {
        console.error("Fehler beim Laden der Cost-Capacity-Daten:", error);
    });
}


document.querySelector('.dropdown-button').addEventListener('click', function() {
        document.querySelector('.dropdown-content').classList.toggle('show');
    });

window.onclick = function(event) {
    if (!event.target.matches('.dropdown-button')) {
        let dropdowns = document.getElementsByClassName("dropdown-content");
        for (let i = 0; i < dropdowns.length; i++) {
            let openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
};

function showCostCapData() {
    costCapContainer = document.getElementById("cost-cap-container")
    if (costCapContainer) {
        costCapContainer.classList.add("active");
    }
}

document.querySelectorAll('.dropdown-content a').forEach(item => {
    item.addEventListener('click', function(event) {
        event.preventDefault();

        const selectedType = this.getAttribute('type');
        loadCostCapacityData(selectedType);
        showCostCapData();

        document.querySelector('.dropdown-content').classList.remove('show');

        document.querySelector('.dropdown-button').textContent = selectedType;
    });
});
