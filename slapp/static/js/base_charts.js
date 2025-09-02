
const techMap = JSON.parse(document.getElementById("technologies").innerText);

async function loadBasicData(region) {
    const url = `/explorer/basic_charts/?type=${encodeURIComponent(region)}`;
    try {
        const response = await fetch(url, { method: 'GET', headers: { "Accept": "application/json" } });
        if (!response.ok) throw new Error("Netzwerkfehler: " + response.status);
        const data = await response.json();
        createElectricityImportChart(data.electricity_import);
        createGenerationConsumptionChart(data.generation_consumption_per_sector);
        createOptimizedCapacitiesChart(data.optimized_capacities);
        createSelfGenerationPowerChart(data.self_generation_imports);
        createSuppliedHoursChart(data.supplied_hours);
        createTotalElectricityChart(data.total_electricity_per_technology);
    } catch (error) {
        console.error("Fehler beim Laden der Basisdaten:", error);
    }
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


function createElectricityImportChart(data) {
  const chart = getOrCreateChart(document.getElementById("electricityImportChart"));
  var option = {
      title: {
          text: 'Stromimport vs. Export',
          left: 'center',
          top: 'top'
      },
      color: ['#2080B6', '#67B7E3'],
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
      tooltip: {
          trigger: 'item',
          valueFormatter: function (value) {
              if (value === undefined) return;
              return value.toString().replace('.', ',') + ' GWh';
          },
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
  const chart = getOrCreateChart(document.getElementById("generationConsumptionChart"));
  const getSeries = ({ data1, center, startAngle = 10 }) => {
    const series = Object.entries(data1).map(([techKey, val]) => {
      const mapEntry = techMap[techKey] || {};
      return {
        name:  mapEntry.name  || techKey,
        value: val,
        ...(mapEntry.color && { itemStyle: { color: mapEntry.color } })
      };
    });
      return {
          type: 'pie',
          radius: '20%',
          center,
          startAngle,
          avoidLabelOverlap: true,
          data: series,
          label: {
              show: true,
              position: 'outside',
              formatter: function (params) {
                  if (params.name !== 'empty') {
                      return params.percent.toString().replace('.', ',') + ' %';
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
              text: `Gesamtstrombedarf (` + data['chart1-total'].toString().replace('.', ',') + ' GWh)',
              left: '25%',
              top: '10%',
              textAlign: 'center', ...subTitleStyle
          },
          {
              text: `Gesamtwärmebedarf dezentral (` + data['chart2-total'].toString().replace('.', ',') + ' GWh)',
              left: '75%',
              top: '10%',
              textAlign: 'center', ...subTitleStyle
          },
          {
              text: `Gesamtwärmebedarf zentral (` + data['chart3-total'].toString().replace('.', ',') + ' GWh)',
              left: '25%',
              top: '55%',
              textAlign: 'center', ...subTitleStyle
          },
          {
              text: `Gesamtwärmebedarf hoch (` + data['chart4-total'].toString().replace('.', ',') + ' GWh)',
              left: '75%',
              top: '55%',
              textAlign: 'center', ...subTitleStyle
          },
      ],
      tooltip: {
          trigger: 'item',
          formatter: function(params) {return params.name + " " + params.value.toString().replace('.', ',') + " GWh (" + params.percent.toString().replace('.', ',') + " %)";}
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
  const chart = getOrCreateChart(document.getElementById("optimizedCapacitiesChart"));

  const sortedMapKeys = Object.keys(techMap).sort((a, b) => b.length - a.length);

  const categories = data.map(item => {
    const foundKey = sortedMapKeys.find(k => item.name.includes(k));
    return foundKey ? techMap[foundKey].name : item.name;
  });

  let option = {
     grid: {
        containLabel: true,
        bottom: '8%'
      },
      title: {
          text: 'Optimierte Kapazitäten',
          left: 'center',
          top: 'top'
      },
      color: ['#2080B6', '#67B7E3'],
      legend: {
          left: 'center',
          top: 'bottom',
      },
      tooltip: {
          trigger: 'axis',
          valueFormatter: function (value) {
              if (value === undefined) return;
              return value.toString().replace('.', ',') + ' MW';
          },
          axisPointer: {
              type: 'cross',
              crossStyle: {
                  color: '#999'
              }
          }
      },
      xAxis: {
          type: 'category',
          data: categories,
          axisLabel: {
              interval: 0,
              rotate: 90,
              margin: 8,
              formatter: function(value) {
                const maxLen = 12;
                return value.length > maxLen ? value.slice(0, maxLen) + '…' : value;
              }
          }
      },
      yAxis: [
          {
              type: 'value',
              name: 'optimierte \n Leistung [MW]',
              nameTextStyle: {
                align: "left"
              }
          },
          {
              type: 'value',
              name: 'theoretisches \n Ausbaupotential [MW]',
              nameTextStyle: {
                align: "right"
              }
          }
      ],
      series: [
          {
              name: 'optimierte Leistung',
              data: data.map(item => item.var_value === 0 ? null : item.var_value),
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
  const chart = getOrCreateChart(document.getElementById("selfGenerationPowerChart"));

  let option = {
      color: ['#2080B6', '#67B7E3'],
      title: {
          text: 'Eigenerzeugung/Stromimporte ',
          subtext: 'Eigenerzeugung + Stromimporte = ' + data.x.toString().replace('.', ',') + ' GWh',
          left: 'center',
          top: 'top'
      },
      tooltip: {
          trigger: 'item',
          valueFormatter: function (value) {
              if (value === undefined) return;
              return value.toString().replace('.', ',') + ' GWh';
          },
      },
      series: [
          {
              type: 'pie',
              radius: "50%",
              data: [
                  {value: data.y1, name: 'Anteil Eigenerzeugung aus EE'},
                  {value: data.y2, name: 'Anteil Stromimport'},
              ],
              label: {
                  show: true,
                  position: 'outside',
                  formatter: function (params) {
                      return params.name + '\n' + params.percent.toString().replace('.', ',') + ' %';
                  },
                  textStyle: {
                      fontSize: 12,
                  },
              }
          },

      ]
  };

  chart.setOption(option);
}

function createSuppliedHoursChart(data) {
  const chart = getOrCreateChart(document.getElementById("suppliedHoursChart"));

  let option = {
      title: {
          text: 'Stunden eigenversorgt/nicht-eigenversorgt',
          left: 'center',
          top: 'top'
      },
      color: ['#2080B6', '#67B7E3'],
      legend: {
          left: 'center',
          top: 'bottom'
      },
      xAxis: {
          type: 'category',
          data: [""]
      },
      yAxis: {
          type: 'value',
          name: 'Prozent (%)',
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
                      return (params.data * 1).toFixed(2).toString().replace('.', ',') + ' %';
                  }
              }

          }
      ]
  };

  chart.setOption(option);
}

function createTotalElectricityChart(data) {
  const chart = getOrCreateChart(document.getElementById("totalElectricityChart"));

  const styledData = data.map(item => {
    const mapEntry = techMap[item.name];
    if (mapEntry) {
      return {
        value: item.value,
        name:  mapEntry.name,
        itemStyle: { color: mapEntry.color }
      };
    }
    return item;
  });

  let option = {
      title: {
          text: 'Stromversorgung je Technologie',
          left: 'center'
      },
      tooltip: {
          trigger: 'item',
          valueFormatter: function (value) {
              if (value === undefined) return;
              return value.toString().replace('.', ',') + ' GWh';
          },
      },
      series: [
          {
              name: 'Energy',
              type: 'pie',
              radius: '50%',
              data: styledData,
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
