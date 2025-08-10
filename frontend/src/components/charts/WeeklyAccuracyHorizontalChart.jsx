import React from 'react';
import ReactApexChart from 'react-apexcharts';

const WeeklyAccuracyHorizontalChart = ({chartData = [], categories = []}) => {
    const series = [{
        name: 'Accuracy',
        data: chartData
    }];

    const options = {
        colors: ['#6C9A8B'],
        chart: {
            type: 'bar',
            height: 300,
            offsetY: 0,
            toolbar: {
                show: false
            }
        },
        plotOptions: {
            bar: {
                borderRadius: 4,
                borderRadiusApplication: 'end',
                horizontal: true,
            }
        },
        dataLabels: {
            enabled: true,
            formatter: (val) => val + "%",
            style: {
                fontSize: '20px',
                fontFamily: '"Noto Sans KR", sans-serif',
                colors: ["#ffffff"]
            },
        },
        xaxis: {
            categories: categories,
            crosshairs: {
                fill: {
                    type: 'gradient',
                    gradient: {
                        colorFrom: '#D8E3F0',
                        colorTo: '#BED1E6',
                        stops: [0, 100],
                        opacityFrom: 0.4,
                        opacityTo: 0.5,
                    }
                }
            },
            tooltip: {enabled: true},
            labels: {
                style: {
                    fontSize: '18px',
                    fontWeight: '500',
                    fontFamily: '"Noto Sans KR", sans-serif',
                }
            }
        },
        yaxis: {
            min: 0,
            max: 100,
            labels: {
                style: {
                    fontSize: '18px',
                    fontWeight: '700',
                    fontFamily: '"Noto Sans KR", sans-serif',
                },
                offsetY: 5
            }
        },
    };

    return (
        <div>
            <div id="chart">
                <ReactApexChart
                    options={options}
                    series={series}
                    type="bar"
                    height={300}
                />
            </div>
            <div id="html-dist"></div>
        </div>
    );
};

export default WeeklyAccuracyHorizontalChart;