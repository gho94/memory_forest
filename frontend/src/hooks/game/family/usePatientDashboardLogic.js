import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { dateUtils } from '@/utils/dateUtils';

export const usePatientDashboardLogic = () => {
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState({
        stats: true,
        chart: true,
        games: true
    });
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');

    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const userId = queryParams.get('userId');
    const gameId = queryParams.get('gameId');

    const fetchPatientDetailData = async (params = {}) => {
        try {
            // 로딩 상태를 세분화해서 관리
            setLoading({ stats: true, chart: true, games: true });

            const queryParams = new URLSearchParams({
                userId,
                ...(gameId && { gameId }),
                ...(params.startDate && { startDate: params.startDate }),
                ...(params.endDate && { endDate: params.endDate })
            });

            const response = await fetch(`${window.API_BASE_URL}/companion/game/dashboard?${queryParams}`);
            const data = await response.json();
            setDashboardData(data);

            // 단계적으로 로딩 해제 (자연스러운 UX를 위해)
            setTimeout(() => setLoading(prev => ({ ...prev, stats: false })), 200);
            setTimeout(() => setLoading(prev => ({ ...prev, chart: false })), 500);
            setTimeout(() => setLoading(prev => ({ ...prev, games: false })), 800);

            if (data.searchDate) {
                const endDateStr = dateUtils.parseSearchDate(data.searchDate);
                if (endDateStr) {
                    setEndDate(endDateStr);
                    setStartDate(dateUtils.getWeekStartDate(endDateStr));
                }
            }
        } catch (error) {
            console.error('Dashboard API 호출 실패:', error);
            // 에러가 나도 로딩 상태는 해제
            setLoading({ stats: false, chart: false, games: false });
        }
    };

    useEffect(() => {
        fetchPatientDetailData();
    }, [userId, gameId]);

    useEffect(() => {
        if (endDate) {
            setStartDate(dateUtils.getWeekStartDate(endDate));
        }
    }, [endDate]);

    // 검색 버튼 클릭 핸들러
    const handleSearch = () => {
        if (startDate && endDate) {
            fetchPatientDetailData({ startDate, endDate });
        } else {
            alert('시작 날짜와 종료 날짜를 모두 선택해주세요.');
        }
    };

    return {
        dashboardData,
        loading,
        startDate,
        endDate,
        setStartDate,
        setEndDate,
        handleSearch,
        fetchPatientDetailData
    };
};