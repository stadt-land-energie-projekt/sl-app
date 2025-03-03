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
        method: 'GET',
        mode: 'cors',
        headers: { 'Accept': 'application/json' },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        let el = document.getElementById("electricity-charts");
        if (!el) return;

        let chart = getOrCreateChart(el);

        let minEnergy = Math.min(...data.energyData.map(d => d.value));
        let maxEnergy = Math.max(...data.energyData.map(d => d.value));

        console.log("max: " + maxEnergy)
        console.log("min: " + minEnergy)

        function scaleLineWidth(value) {
            const diff = maxEnergy - minEnergy;
            if (diff === 0) {
                return 4;
            } else {
                return 1 + ((value - minEnergy) / diff) * 7;
            }
        }

        let option = {
            title: {
                text: data.title || 'Stromaustausch zwischen Regionen',
                left: 'center'
            },
            tooltip: {
                trigger: 'item',
                formatter: function (params) {
                    if (params.dataType === 'edge') {
                        return `${params.data.source} → ${params.data.target}: ${params.data.value} MWh`;
                    }
                    return params.name;
                }
            },
            series: [
                {
                    type: 'graph',
                    force: {
                        repulsion: 300,
                        edgeLength: [50, 200]
                    },
                    roam: true,
                    label: {
                        show: true,
                        position: 'right',
                        fontSize: 20
                    },
                    edgeSymbol: ['none', 'arrow'],
                    edgeSymbolSize: 10,
                    lineStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                            { offset: 0, color: '#feb1b1' },
                            { offset: 1, color: '#c34747' }
                        ]),
                        curveness: 0.2,
                        opacity: 0.8
                    },
                    data: data.nodes,
                    links: data.energyData.map(d => ({
                        source: d.source,
                        target: d.target,
                        value: d.value,
                        lineStyle: {
                            width: scaleLineWidth(d.value)
                        }
                    })),
                    emphasis: {
                        focus: 'adjacency'
                    }
                }
            ]
        };

        chart.setOption(option);
        chart.resize();
    })
    .catch(error => {
        console.error("Error loading flow chart:", error);
    });
}

function showHiddenDiv(chartType, button) {
    let allButtons = document.querySelectorAll(".select-button");
    allButtons.forEach(b => b.classList.remove("selected"));

    button.classList.add("selected");

    let hiddenDiv = document.querySelector(".hidden-div");
    hiddenDiv.style.display = "block";

    loadFlowsChart(chartType);
    }
