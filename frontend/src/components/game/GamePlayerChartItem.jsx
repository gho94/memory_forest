import React from 'react';
import WeeklyAccuracyHorizontalChart from '@/components/charts/WeeklyAccuracyHorizontalChart';
import PatientDetailChartSkeleton from '@/components/skeleton/PatientDetailChartSkeleton';

const GamePlayerChartItem = ({
                                 loading,
                                 chartData,
                                 includeGameId,
                                 showToggleButton,
                                 onToggleGameId
                             }) => {
    return (
        <section className="content-con chart-section">
            <div className="chart-con">
                <div className="chart-header">
                    <h3>게임 일주일 정답률</h3>
                    {showToggleButton && (
                        <div className="toggle-button-con">
                            <button
                                onClick={onToggleGameId}
                                className="toggle-button"
                            >
                                {includeGameId ? '게임 시점' : '최근 7일'}
                            </button>
                        </div>
                    )}
                </div>
                <div className="chart">
                    {loading.chart ? (
                        <PatientDetailChartSkeleton/>
                    ) : (
                        <WeeklyAccuracyHorizontalChart
                            chartData={chartData.data}
                            categories={chartData.categories}
                        />
                    )}
                </div>
            </div>
        </section>
    );
};

export default GamePlayerChartItem;