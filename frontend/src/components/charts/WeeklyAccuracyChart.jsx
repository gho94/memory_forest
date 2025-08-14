import React from 'react';
import ReactApexChart from 'react-apexcharts';

const WeeklyAccuracyChart = ({ chartData = [], categories = [], chartTitle, format, dataTitle }) => {
    const options = {
        colors: ['#4ec2e8'],
        chart: {
            height: 350,
            type: 'bar',
        },
        plotOptions: {
            bar: {
                borderRadius: 10,
                dataLabels: {
                    position: 'top',
                },
            },
        },
        dataLabels: {
            enabled: true,
            formatter: (val) => val + format,
            offsetY: -20,
            style: {
                fontSize: '12px',
                colors: ["#304758"]
            },
        },
        xaxis: {
            categories: categories,
            position: 'bottom',
            axisBorder: { show: false },
            axisTicks: { show: false },
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
            tooltip: { enabled: true },
            labels: {
                style: {
                    fontSize: '10px',
                }
            }
        },
        yaxis: {
            min: 0,
            max: 105,
            axisBorder: { show: false },
            axisTicks: { show: false },
            labels: {
                show: false,
                formatter: (val) => val + "%",
            }
        },
        title: {
            text: chartTitle,
            floating: true,
            offsetY: 0,
            align: 'center',
            style: { color: '#444'}
        }
    };

    const series = [{
        name: dataTitle,
        data: chartData
    }];

    return (
        <div>
            <div id="chart">
                <ReactApexChart options={options} series={series} type="bar" height={350} />
            </div>
        </div>
    );
};

export default WeeklyAccuracyChart;