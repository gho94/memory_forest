import React from 'react';
import PatientDetailStatSkeleton from '@/components/skeleton/PatientDetailStatSkeleton';
import WeeklyAccuracyChart from '@/components/charts/WeeklyAccuracyChart';
import PatientDetailChartSkeleton from '@/components/skeleton/PatientDetailChartSkeleton';

function RecordChartAndDataItem({ chartData, loading, searchDate, record }) {
    return (
        <div className="chart-con">
            <div className="chart">
                {loading.chart ? (
                    <PatientDetailChartSkeleton />
                ) : (
                    <WeeklyAccuracyChart
                        chartData={chartData.data}
                        categories={chartData.categories}
                        chartTitle={'기록 감정 긍정 점수'}
                        format={'점'}
                        dataTitle={'긍정 점수'}
                    />
                )}
            </div>
            <div className="game-result">
                <div className="game-date">{searchDate || ''}</div>
                {loading.record ? (
                    <>
                        <PatientDetailStatSkeleton />
                    </>
                ) : record ? (
                    <>
                        {record.audioUrl && (
                            <audio
                                controls
                                className="ms-2"
                                style={{height: '38px'}}
                                preload="metadata"
                            >
                                <source src={record.audioUrl} type="audio/wav"/>
                                브라우저가 오디오를 지원하지 않습니다.
                            </audio>
                        )}
                        <div className="p-4 text-start">{record.text}</div>
                    </>
                ) : (
                    // 게임이 없을 때
                    <div className="no-game-message">진행된 기록이 존재하지 않습니다.</div>
                )}
            </div>
        </div>
    );
}

export default RecordChartAndDataItem;