function createElectricityImportChart(data) {
        const chart = getOrCreateChart("electricityImportChart");
        var option = {
            title: {
                text: 'Stromimport vs. Export',
                left: 'center',
                top: 'top'
            },
            legend: {
                left: 'center',
                top: 'bottom'
            },
            xAxis: {
                type: 'category',
                data: ['Importe', "Exporte"]
            },
            yAxis: {
                type: 'value',
                name: 'GWh'
            },
            series: [
                {
                    data: data,
                    type: 'bar'
                }
            ]
        };
        chart.setOption(option);
    }

function createGenerationConsumptionChart(data) {
    const chart = getOrCreateChart("generationConsumptionChart");
    const getSeries = ({data1, name, center}) => {
        let series = [];
        for (const [k, v] of Object.entries(data1)) {
            series.push({name: k, value: v});
        }
        return {
            type: 'pie',
            radius: '20%',
            center,
            data: series,
            label: {
                show: true,
                position: 'outside',
                formatter: function (params) {
                    if (params.name !== 'empty') {
                        return params.percent + '%';
                    }
                    return '';
                },
                textStyle: {
                    fontSize: 12,
                }
            }
        };
    };

    const subTitleStyle = {
        textStyle: {
            fontSize: 12,
            fontWeight: '400',
            color: '#333'
        }
    };

    const option = {
        title: [
            {
                text: 'Erzeugung vs Verbrauch je Sektor ',
                left: 'center',
                top: 'top'
            },
            {
                text: `flow_out_electricity von TechnologieX \n / Gesamtstrombedarf (` + data['chart1-total'] + 'GW)',
                left: '25%',
                top: '10%',
                textAlign: 'center', ...subTitleStyle
            },
            {
                text: `flow_out_heat_low_decentral von TechnologieX  \n / Gesamtwämrebedarf dezentral (` + data['chart2-total'] + 'GW)',
                left: '75%',
                top: '10%',
                textAlign: 'center', ...subTitleStyle
            },
            {
                text: `flow_out_heat_low_central von TechnologieX \n / Gesamtwämrebedarf zentral (` + data['chart3-total'] + 'GW)',
                left: '25%',
                top: '55%',
                textAlign: 'center', ...subTitleStyle
            },
            {
                text: `flow_out_heat_high von TechnologieX \n / Gesamtwämrebedarf heat_high (` + data['chart4-total'] + 'GW)',
                left: '75%',
                top: '55%',
                textAlign: 'center', ...subTitleStyle
            },
        ],
        tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        series: [
            getSeries({
                data1: data['chart1-1'],
                name: 'electricity',
                center: ['25%', '30%']
            }),
            getSeries({
                data1: data['chart2-1'],
                name: 'electricity1',
                center: ['75%', '30%']
            }),
            getSeries({
                data1: data['chart3-1'],
                name: 'electricity2',
                center: ['25%', '75%']
            }),
            getSeries({
                data1: data['chart4-1'],
                name: 'electricity3',
                center: ['75%', '75%']
            }),

        ]
    };
    chart.setOption(option);
}

function createOptimizedCapacitiesChart(data) {
    const chart = getOrCreateChart("optimizedCapacitiesChart");

    let option = {
        title: {
            text: 'Optimierte Kapazitäten',
            left: 'center',
            top: 'top'
        },
        legend: {
            left: 'center',
            top: 'bottom'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                crossStyle: {
                    color: '#999'
                }
            }
        },
        xAxis: {
            type: 'category',
            data: data.map(item => item.name),
            axisLabel: {
                interval: 0,
                rotate: 90,
            }
        },
        yAxis: [
            {
                type: 'value',
                name: 'optimierte \n Leistung [MW]',
            },
            {
                type: 'value',
                name: 'theoretisches \n Ausbaupotential [MW]',
            }
        ],
        series: [
            {
                name: 'optimierte Leistung',
                data: data.map(item => item.var_value === 0 ? item.capacity_potential * 0.5 : item.var_value),
                type: 'bar'
            },
            {
                name: 'theoretisches Ausbaupotential',
                data: data.map(item => item.capacity_potential),
                type: 'scatter'
            }
        ]
    };

    chart.setOption(option);
}

function createSelfGenerationPowerChart(data) {
    const chart = getOrCreateChart("selfGenerationPowerChart");

    let option = {
        title: {
            text: 'Eigenerzeugung/Stromimporte ',
            subtext: 'Eigenerzeugung + Stromimporte = ' + data.x + 'GWh',
            left: 'center',
            top: 'top'
        },
        legend: {
            left: 'center',
            top: 'bottom'
        },

        series: [
            {
                type: 'pie',
                data: [
                    {value: data.y1, name: 'Anteil Eigenerzeugung aus EE'},
                    {value: data.y2, name: 'Anteil Stromimport'},
                ],
                label: {
                    show: true,
                    position: 'outside',
                    formatter: function (params) {
                        return params.name + '\n' + params.percent + '%';
                    },
                    textStyle: {
                        fontSize: 12,
                    }
                }
            },

        ]
    };

    chart.setOption(option);
}

function createSuppliedHoursChart(data) {
    const chart = getOrCreateChart("suppliedHoursChart");

    let option = {
        title: {
            text: 'Stunden eigenversorgt/nicht-eigenversorgt',
            left: 'center',
            top: 'top'
        },
        legend: {
            left: 'center',
            top: 'bottom'
        },
        xAxis: {
            type: 'category',
            data: Object.keys(data.y1)
        },
        yAxis: {
            type: 'value',
            name: 'Percentage (%)',
            axisLabel: {formatter: '{value}%'}
        },
        series: [
            {
                name: 'Stunden mit Eigenerzeugung',
                type: 'bar',
                stack: 'total',
                data: Object.values(data.y1),
                label: {
                    show: true,
                    position: 'inside',
                    formatter: function (params) {
                        return (params.data * 1).toFixed(2) + '%';
                    }
                }
            },
            {
                name: 'Stunden ohne Eigenversorgung',
                type: 'bar',
                stack: 'total',
                data: Object.values(data.y2),
                label: {
                    show: true,
                    position: 'inside',
                    formatter: function (params) {
                        return (params.data * 1).toFixed(2) + '%';
                    }
                }

            }
        ]
    };

    chart.setOption(option);
}

function createTotalElectricityChart(data) {
    const chart = getOrCreateChart("totalElectricityChart");

    let option = {
        title: {
            text: 'Referer of a Website',
            subtext: 'Fake Data',
            left: 'center'
        },
        tooltip: {
            trigger: 'item'
        },
        legend: {
            orient: 'vertical',
            left: 'left'
        },
        series: [
            {
                name: 'Access From',
                type: 'pie',
                radius: '50%',
                data: data,
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

    chart.setOption(option);
}
