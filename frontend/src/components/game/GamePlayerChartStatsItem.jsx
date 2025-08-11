import React from 'react';
import PatientDetailStatSkeleton from '@/components/skeleton/PatientDetailStatSkeleton';

const GamePlayerChartStatsItem = ({ loading, statsData }) => {
    return (
        <div className="row">
            <div className="col-6">
                <section className="content-con chart-section">
                    {loading.stats ? (
                        <PatientDetailStatSkeleton />
                    ) : (
                        <>
                            <div className="result-number">{statsData.totalGames}</div>
                            <div className="result-text">총 게임 횟수</div>
                        </>
                    )}
                </section>
            </div>
            <div className="col-6">
                <section className="content-con chart-section">
                    {loading.stats ? (
                        <PatientDetailStatSkeleton />
                    ) : (
                        <>
                            <div className="result-number">{statsData.averageAccuracy}%</div>
                            <div className="result-text">평균<br />정답률</div>
                        </>
                    )}
                </section>
            </div>
        </div>
    );
};

export default GamePlayerChartStatsItem;