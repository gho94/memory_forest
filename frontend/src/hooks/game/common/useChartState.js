import React, { useState, useEffect } from 'react';
import {usePatientOverviewLogic} from '@/hooks/game/common/usePatientOverviewLogic';

export const useChartState = (gameIdFromUrl) => {
    const [includeGameId, setIncludeGameId] = useState(true);
    const [dashboardData, setDashboardData] = useState(null);
    const [statsData, setStatsData] = useState({
        totalGames: 0,
        averageScore: 0
    });

    const { loading, fetchChartData, fetchStatsData } = usePatientOverviewLogic();

    // 차트 데이터 가져오기 (내부에서 사용)
    const loadChartData = async (useGameId = includeGameId) => {
        try {
            const chartData = await fetchChartData(useGameId, gameIdFromUrl);
            setDashboardData(chartData);
        } catch (error) {
            console.error('차트 로딩 실패:', error);
        }
    };

    // 통계 데이터 가져오기 (내부에서 사용)
    const loadStatsData = async () => {
        try {
            const statsData = await fetchStatsData();
            setStatsData(statsData);
        } catch (error) {
            console.error('통계 로딩 실패:', error);
        }
    };

    // 토글 핸들러
    const handleToggleGameId = () => {
        const newIncludeGameId = !includeGameId;
        setIncludeGameId(newIncludeGameId);
        loadChartData(newIncludeGameId);
    };

    // 초기 로딩
    useEffect(() => {
        loadChartData();
        loadStatsData();
    }, []);

    return {
        // 상태
        includeGameId,
        dashboardData,
        statsData,
        loading,

        // 액션
        handleToggleGameId
    };
};