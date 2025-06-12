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

    const selectedNameElement = document.querySelector("#cs-details #cs-selected-name");
    if (selectedNameElement) {
        selectedNameElement.textContent = regionTitle;
    }

    load_charts(regionTitle);
    console.log("region titel: " + regionTitle);
    display_details(regionTitle);
    updateStickyHeader(regionTitle);
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
        load_capacity_chart(data.capacity);
        load_capacity_potential_chart(data.capacity_potential);
        load_capacity_potential_usage_chart(data.capacity_potential_usage)
        load_production_chart(data.production);
        load_production_specific_chart(data.production_specific);
        load_demand_power_chart(data.demand_power);
        load_self_generation_power_chart(data.self_generation);
        load_demand_heat_chart(data.demand_heat);
        load_demand_heat_type_chart(data.demand_heat_type);
        load_area_chart(data.area);
        load_population_chart(data.population);
    })
    .catch(error => {
        console.error("Error loading charts:", error);
    });
}

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

function load_capacity_chart(chartData) {
    let el = document.getElementById("chart-capacity");
    if (!el) return;

    let chart = getOrCreateChart(el);

    let series = [];
    for (let [name, values] of Object.entries(chartData.y_data)) {
        series.push({ name: name, data: values, type: 'bar' });
    }

    // // Optional: a line for a "target" value
    // if (chartData.target) {
    //     for (let [targetLabel, targetVal] of Object.entries(chartData.target)) {
    //         series.push({
    //             name: targetLabel,
    //             type: 'line',
    //             markLine: {
    //                 symbol: 'none',
    //                 data: [{ yAxis: targetVal }]
    //             },
    //         });
    //     }
    // }

    let options = {
        title: { text: "Installierte Leistung EE (Strom)" },
        color: ['#67B7E3', '#F0C808', '#F9E171', '#4AC29D'],
        tooltip: {
            trigger: 'axis',
            valueFormatter: function (value) {
                return `${value} MW`.replace('.', ',');
            }
        },
        legend: {
            orient: 'horizontal',
            left: 'center',
            bottom: '5%',
        },
        xAxis: { type: "category", data: chartData.x_data },
        yAxis: { type: "value", name: chartData.y_label || "" },
        series: series
    };

    chart.setOption(options);
    chart.resize();
}

function load_capacity_potential_chart(chartData) {
    let el = document.getElementById("chart-capacity-potential");
    if (!el) return;

    let chart = getOrCreateChart(el);

    let series = [];
    for (let [name, values] of Object.entries(chartData.y_data)) {
        series.push({ name: name, data: values, type: 'bar' });
    }

    let options = {
        title: { text: "Installierbare Leistung EE (Strom)" },
        color: ['#67B7E3', '#F0C808', '#F9E171'],
        tooltip: {
            trigger: 'axis',
            valueFormatter: function (value) {
                return `${value} MW`.replace('.', ',');
            }
        },
        legend: {
            orient: 'horizontal',
            left: 'center',
            bottom: '5%',
        },
        xAxis: { type: "category", data: chartData.x_data },
        yAxis: { type: "value", name: chartData.y_label || "" },
        series: series
    };

    chart.setOption(options);
    chart.resize();
}

function load_capacity_potential_usage_chart(chartData) {
    let el = document.getElementById("chart-capacity-potential-usage");
    if (!el) return;

    let chart = getOrCreateChart(el);

    let series = [];
    for (let [name, values] of Object.entries(chartData.y_data)) {
        series.push({ name: name, data: values, type: 'bar' });
    }

    let options = {
        title: { text: "Potenzialnutzung EE" },
        color: ['#67B7E3', '#F0C808', '#F9E171'],
        tooltip: {
            trigger: 'axis',
            valueFormatter: function (value) {
                return `${value} %`.replace('.', ',');
            }
        },
        legend: {
            orient: 'horizontal',
            left: 'center',
            bottom: '5%',
        },
        xAxis: { type: "category", data: chartData.x_data },
        yAxis: { type: "value", name: chartData.y_label || "" },
        series: series
    };

    chart.setOption(options);
    chart.resize();
}

function load_production_chart(chartData) {
    let el = document.getElementById("chart-production");
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
        title: { text: "Stromerzeugung aus EE" },
        color: ['#67B7E3', '#F0C808', '#F9E171', '#4AC29D'],
        tooltip: {
            trigger: 'axis',
            valueFormatter: function (value) {
                return `${value} GWh`.replace('.', ',');
            }
        },
        legend: {
            orient: 'horizontal',
            left: 'center',
            bottom: '5%',
        },
        xAxis: { type: "category", data: chartData.x_data },
        yAxis: { type: "value", name: chartData.y_label || "" },
        series: series
    };

    chart.setOption(options);
    chart.resize();
}

function load_production_specific_chart(chartData) {
    let el = document.getElementById("chart-production-specific");
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
        title: { text: "Stromerzeugung aus EE spezifisch" },
        color: ['#21A179', '#73DDBC'],
        tooltip: {
            trigger: 'axis',
            valueFormatter: function (value) {
                return `${value} MWh`.replace('.', ',');
            }
        },
        legend: {
            orient: 'horizontal',
            left: 'center',
            bottom: '5%',
        },
        xAxis: { type: "category", data: chartData.x_data },
        yAxis: { type: "value", name: chartData.y_label || "" },
        series: series
    };

    chart.setOption(options);
    chart.resize();
}

function load_demand_power_chart(chartData) {
    let el = document.getElementById("chart-demand-power");
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
        title: { text: "Strombedarf (ohne Wärme)" },
        color: ['#2080B6', '#67B7E3', '#BAE1F6'],
        // backgroundColor: '#E9F6FE',
        tooltip: {
            trigger: 'axis',
            valueFormatter: function (value) {
                return `${value} GWh`.replace('.', ',');
            }
        },
        legend: {
            orient: 'horizontal',
            left: 'center',
            bottom: '5%',
        },
        xAxis: { type: "category", data: chartData.x_data },
        yAxis: { type: "value", name: chartData.y_label || "" },
        series: series
    };

    chart.setOption(options);
    chart.resize();
}

function load_self_generation_power_chart(chartData) {
    let el = document.getElementById("chart-self-generation-power");
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
        title: { text: "Strombedarfsdeckung aus EE bilanziell" },
        color: ['#2080B6'],
        // backgroundColor: '#F6FCFF',
        tooltip: {
            trigger: 'axis',
            valueFormatter: function (value) {
                return `${value} %`.replace('.', ',');
            }
        },
        legend: {
            orient: 'horizontal',
            left: 'center',
            bottom: '5%',
        },
        xAxis: { type: "category", data: chartData.x_data },
        yAxis: { type: "value", name: chartData.y_label || "" },
        series: series
    };

    chart.setOption(options);
    chart.resize();
}


function load_demand_heat_chart(chartData) {
    let el = document.getElementById("chart-demand-heat");
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
        title: { text: "Wärmebedarf" },
        color: ['#AB2134', '#E5707F', '#FAC7CD'],
        // backgroundColor: '#FFF6F8',
        tooltip: {
            trigger: 'axis',
            valueFormatter: function (value) {
                return `${value} GWh`.replace('.', ',');
            }
        },
        legend: {
            orient: 'horizontal',
            left: 'center',
            bottom: '5%',
        },
        xAxis: { type: "category", data: chartData.x_data },
        yAxis: { type: "value", name: chartData.y_label || "" },
        series: series
    };

    chart.setOption(options);
    chart.resize();
}

function load_demand_heat_type_chart(chartData) {
    let el = document.getElementById("chart-demand-heat-type");
    if (!el) return;

    let chart = getOrCreateChart(el);

    let pieData = [];
    for (let [key, valArray] of Object.entries(chartData.y_data)) {
        let val = (valArray && valArray.length > 0) ? valArray[0] : 0;
        pieData.push({ name: key, value: val });
    }

    let options = {
        title: { text: "Art der Wärmversorgung", left: 'center' },
        color: ['#AB2134', '#E5707F'],
        // backgroundColor: '#FFF6F8',
        tooltip: {
            trigger: 'item',
            valueFormatter: function (value) {
                return `${value} %`.replace('.', ',');
            }
        },
        legend: {
            show: false
        },
        series: [
            {
                name: "Area",
                type: 'pie',
                radius: ['40%', '70%'],
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

function load_area_chart(chartData) {
    let el = document.getElementById("chart-area");
    if (!el) return;

    let chart = getOrCreateChart(el);

    let pieData = [];
    for (let [key, valArray] of Object.entries(chartData.y_data)) {
        let val = (valArray && valArray.length > 0) ? valArray[0] : 0;
        pieData.push({ name: key, value: val });
    }

    let options = {
        title: { text: "Regionsfläche", left: 'center' },
        color: ['#758E9A', '#99ACB5', '#BECAD0', '#E3E8EB'],
        tooltip: {
            trigger: 'item',
            valueFormatter: function (value) {
                return `${value} km²`.replace('.', ',');
            }
        },
        legend: {
            show: false
        },
        series: [
            {
                name: "Area",
                type: 'pie',
                radius: ['40%', '70%'],
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

function load_population_chart(chartData) {
    let el = document.getElementById("chart-population");
    if (!el) return;

    let chart = getOrCreateChart(el);

    let pieData = [];
    for (let [key, valArray] of Object.entries(chartData.y_data)) {
        let val = (valArray && valArray.length > 0) ? valArray[0] : 0;
        pieData.push({ name: key, value: val });
    }

    let options = {
        title: { text: "Bevölkerung", left: 'center' },
        color: ['#758E9A', '#99ACB5', '#BECAD0', '#E3E8EB'],
        tooltip: {
            trigger: 'item',
            valueFormatter: function (value) {
                return `${value} Personen`.replace('.', ',');
            }
        },
        legend: {
            show: false
        },
        series: [
            {
                name: "Area",
                type: 'pie',
                radius: ['40%', '70%'],
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
      const wrapper = event.currentTarget.closest('.cs__region-container');
      const title   = wrapper.dataset.regionTitle;

      // 2a) Update the sticky header
      updateStickyHeader(title);
    });
  });

  // 3) Show/hide the sticky header when the first card scrolls out of view
 const firstTitle = document.querySelector(
    '.cs__region-container[data-region-title] .cs__top-row h2'
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
