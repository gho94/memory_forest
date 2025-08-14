import React from 'react';
import WeeklyAccuracyChart from '@/components/charts/WeeklyAccuracyChart';
import GamePlayerDetailItem from '@/components/game/GamePlayerDetailItem';
import PatientDetailChartSkeleton from '@/components/skeleton/PatientDetailChartSkeleton';
import PatientDetailStatSkeleton from '@/components/skeleton/PatientDetailStatSkeleton';

const GamePlayerChartAndGameItem = ({ chartData, loading, searchDate, gameList }) => {
    return (
        <div className="chart-con">
            <div className="chart">
                {loading.chart ? (
                    <PatientDetailChartSkeleton />
                ) : (
                    <WeeklyAccuracyChart
                        chartData={chartData.data}
                        categories={chartData.categories}
                        chartTitle={'게임 일주일 정답률'}
                        format={'%'}
                        dataTitle={'정답률'}
                    />
                )}
            </div>
            <div className="game-result">
                <div className="game-date">{searchDate || ''}</div>
                {loading.games ? (
                    // 게임 로딩 중일 때 스켈레톤
                    <>
                        <PatientDetailStatSkeleton />
                        <PatientDetailStatSkeleton />
                        <PatientDetailStatSkeleton />
                    </>
                ) : gameList?.length > 0 ? (
                    // 실제 게임 데이터
                    gameList.map((game, index) => (
                        <GamePlayerDetailItem key={`${game.gameId}-${game.gameSeq}`} game={game} />
                    ))
                ) : (
                    // 게임이 없을 때
                    <div className="no-game-message">진행된 게임이 존재하지 않습니다.</div>
                )}
            </div>
        </div>
    );
};

export default GamePlayerChartAndGameItem;