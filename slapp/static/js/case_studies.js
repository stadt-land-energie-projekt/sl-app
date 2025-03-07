function regionSelected(buttonElement, regionTitle) {
    document.querySelectorAll(".cs__region-container").forEach(container => {
        container.classList.remove("selected");
        const button = container.querySelector("button");
        if (button) {
            if (button.hasAttribute("Auswählen")) {
                button.textContent = button.getAttribute("Auswählen");
            }
        }
    });

    const parentContainer = buttonElement.closest(".cs__region-container");
    parentContainer.classList.add("selected");
    const button = parentContainer.querySelector("button");
    if (button) {
        if (!button.hasAttribute("Auswählen")) {
            button.setAttribute("Auswählen", button.textContent);
        }
        button.textContent = "Ausgewählt";
    }

    load_charts(regionTitle);
    display_details(regionTitle);
}

function display_details(regionTitle){
  const divOs = document.getElementById('table-details-os');
  const divKiel = document.getElementById('table-details-kiel');

  if (regionTitle === "Region Oderland-Spree") {
        divOs.style.display = "block";
        divKiel.style.display = "none";
    } else if (regionTitle === "Region Kiel") {
        divOs.style.display = "none";
        divKiel.style.display = "block";
    } else {
        divOs.style.display = "none";
        divKiel.style.display = "none";
    }
}

function load_charts(regionTitle) {
    let url = window.location.origin + "/explorer/chart/all_charts?region=" + encodeURIComponent(regionTitle);

    fetch(url, {
        method: 'GET',
        mode: 'cors',
        headers: { 'Accept': 'application/json' },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        load_production_chart(data.production);
        load_tech_chart(data.tech);
        load_another_chart(data.another);
        load_demand_chart(data.demand);
        load_area_chart(data.area);
        load_co2_chart(data.co2);
    })
    .catch(error => {
        console.error("Error loading charts:", error);
    });
}

function on_load() {
    load_charts(window.regionTitle);
    display_details(window.regionTitle);
    let firstButton = document.querySelector(".select-button");
    if (firstButton) {
      firstButton.classList.add("selected");
    }
}

on_load();

/**
 * Helper function to either create a new ECharts instance or clear the old one.
 */
function getOrCreateChart(domElement) {
    let chart = echarts.getInstanceByDom(domElement);
    if (chart) {
        chart.clear();
    } else {
        chart = echarts.init(domElement, null, { renderer: "svg" });
    }
    return chart;
}

/**
 * Production chart (simple bar chart)
 */
function load_production_chart(chartData) {
    let el = document.getElementById("chart-production");
    if (!el) return;

    let chart = getOrCreateChart(el);

    let series = [];
    for (let [name, values] of Object.entries(chartData.y_data)) {
        series.push({ name: name, data: values, type: 'bar' });
    }

    let options = {
        title: { text: "Production" },
        tooltip: {},
        legend: {},
        xAxis: { type: "category", data: chartData.x_data },
        yAxis: { type: "value", name: chartData.y_label || "" },
        series: series
    };

    chart.setOption(options);
    chart.resize();
}

/**
 * Tech chart (bar chart with multiple bars side by side)
 */
function load_tech_chart(chartData) {
    let el = document.getElementById("chart-tech");
    if (!el) return;

    let chart = getOrCreateChart(el);

    let series = [];
    for (let [name, values] of Object.entries(chartData.y_data)) {
        series.push({ name: name, data: values, type: 'bar' });
    }

    // Optional: a line for a "target" value
    if (chartData.target) {
        for (let [targetLabel, targetVal] of Object.entries(chartData.target)) {
            series.push({
                name: targetLabel,
                type: 'line',
                markLine: {
                    symbol: 'none',
                    data: [{ yAxis: targetVal }]
                }
            });
        }
    }

    let options = {
        title: { text: "Tech Chart" },
        tooltip: {},
        legend: {},
        xAxis: { type: "category", data: chartData.x_data },
        yAxis: { type: "value", name: chartData.y_label || "" },
        series: series
    };

    chart.setOption(options);
    chart.resize();
}

/**
 * Another chart: also a bar chart
 */
function load_another_chart(chartData) {
    let el = document.getElementById("chart-another");
    if (!el) return;

    let chart = getOrCreateChart(el);

    let series = [];
    for (let [name, values] of Object.entries(chartData.y_data)) {
        series.push({ name: name, data: values, type: 'bar' });
    }

    let options = {
        title: { text: "Another Chart" },
        tooltip: {},
        legend: {},
        xAxis: { type: "category", data: chartData.x_data },
        yAxis: { type: "value", name: chartData.y_label || "" },
        series: series
    };

    chart.setOption(options);
    chart.resize();
}

/**
 * Demand chart: stacked bar chart
 */
function load_demand_chart(chartData) {
    let el = document.getElementById("chart-demand");
    if (!el) return;

    let chart = getOrCreateChart(el);

    let series = [];
    for (let [name, values] of Object.entries(chartData.y_data)) {
        series.push({
            name: name,
            data: values,
            type: 'bar',
            stack: 'demandStack'
        });
    }

    let options = {
        title: { text: "Demand Chart" },
        tooltip: { trigger: 'axis' },
        legend: {},
        xAxis: { type: "category", data: chartData.x_data },
        yAxis: { type: "value", name: chartData.y_label || "" },
        series: series
    };

    chart.setOption(options);
    chart.resize();
}

/**
 * Area chart: pie chart
 */
function load_area_chart(chartData) {
    let el = document.getElementById("chart-area");
    if (!el) return;

    let chart = getOrCreateChart(el);

    // We transform the y_data into an array of {value, name} items for the pie
    let pieData = [];
    for (let [key, valArray] of Object.entries(chartData.y_data)) {
        let val = (valArray && valArray.length > 0) ? valArray[0] : 0;
        pieData.push({ name: key, value: val });
    }

    let options = {
        title: { text: "Area Chart", left: 'center' },
        tooltip: { trigger: 'item' },
        legend: {
            orient: 'horizontal',
            left: 'center',
            top: 'bottom',
        },
        series: [
            {
                name: "Area",
                type: 'pie',
                radius: '50%',
                data: pieData,
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    };

    chart.setOption(options);
    chart.resize();
}

/**
 * CO2 "chart": we only display an icon and some text
 */
function load_co2_chart(co2Data) {
    let co2El = document.getElementById("co2-info");
    if (!co2El) return;

    let iconUrl = co2Data.icon_url || "";
    let text = co2Data.co2_text || "No data";

    co2El.innerHTML = `
        <img src="${iconUrl}" alt="CO2 Icon" style="height:24px; vertical-align:middle;" />
        <span style="margin-left: 8px;">${text}</span>
    `;
}
