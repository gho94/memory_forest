import { useState } from 'react';

export const usePatientOverviewLogic = () => {
    const [loading, setLoading] = useState({
        chart: true,
        stats: true
    });

    const fetchChartData = async (useGameId, gameIdFromUrl) => {
        try {
            const chartUrl = (useGameId && gameIdFromUrl)
                ? `${window.API_BASE_URL}/recorder/game/chart/weekly-chart?gameId=${gameIdFromUrl}`
                : `${window.API_BASE_URL}/recorder/game/chart/weekly-chart`;

            setLoading(prev => ({ ...prev, chart: true }));
            const chartResponse = await fetch(chartUrl, {
                method: 'GET',
                credentials: 'include',
            });
            const chartData = await chartResponse.json();
            setTimeout(() => setLoading(prev => ({ ...prev, chart: false })), 200);
            return chartData;
        } catch (error) {
            console.error('차트 데이터 로딩 실패:', error);
            setLoading(prev => ({ ...prev, chart: false }));
            throw error;
        }
    };

    const fetchStatsData = async () => {
        try {
            setLoading(prev => ({ ...prev, stats: true }));
            const statsResponse = await fetch(`${window.API_BASE_URL}/recorder/game/chart/stats`);
            const statsData = await statsResponse.json();
            setTimeout(() => setLoading(prev => ({ ...prev, stats: false })), 200);
            return statsData;
        } catch (error) {
            console.error('통계 데이터 로딩 실패:', error);
            setLoading(prev => ({ ...prev, stats: false }));
            throw error;
        }
    };

    return {
        loading,
        fetchChartData,
        fetchStatsData
    };
};