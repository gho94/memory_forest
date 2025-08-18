import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { dateUtils } from '@/utils/dateUtils';
import useFileUrl from '@/hooks/common/useFileUrl';

export const usePatientRecordLogic = () => {
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState({
        stats: true,
        chart: true,
        record: true
    });
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [playerName, setPlayerName] = useState('');
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const userId = queryParams.get('userId');
    const { fetchFileUrl, isLoading: fileLoading } = useFileUrl();

    const fetchPatientRecordData = async (params = {}) => {
        try {
            setLoading({ stats: true, chart: true, record: true });

            const queryParams = new URLSearchParams({
                userId,
                ...(params.startDate && { startDate: params.startDate }),
                ...(params.endDate && { endDate: params.endDate })
            });

            const response = await fetch(`${window.API_BASE_URL}/companion/record/dashboard?${queryParams}`);
            const data = await response.json();
            setDashboardData(data);

            if (data.record && data.record.fileId) {
                try {
                    const fileUrl = await fetchFileUrl(data.record.fileId);
                    data.record.audioUrl = fileUrl;
                } catch (error) {
                    console.error('파일 URL 가져오기 실패:', error);
                    data.record.audioUrl = null;
                }
            }

            // 단계적으로 로딩 해제
            setTimeout(() => setLoading(prev => ({ ...prev, stats: false })), 200);
            setTimeout(() => setLoading(prev => ({ ...prev, chart: false })), 500);
            setTimeout(() => setLoading(prev => ({ ...prev, record: false })), 800);

            if (data.searchDate) {
                const endDateStr = dateUtils.parseSearchDate(data.searchDate);
                if (endDateStr) {
                    setEndDate(endDateStr);
                    setStartDate(dateUtils.getWeekStartDate(endDateStr));
                }
            }

            if (data.playerName) setPlayerName(data.playerName);

        } catch (error) {
            console.error('Record Dashboard API 호출 실패:', error);
            setLoading({ stats: false, chart: false, record: false });
        }
    };

    useEffect(() => {
        fetchPatientRecordData();
    }, [userId]);

    useEffect(() => {
        if (endDate) {
            setStartDate(dateUtils.getWeekStartDate(endDate));
        }
    }, [endDate]);

    const handleSearch = () => {
        if (startDate && endDate) {
            fetchPatientRecordData({ startDate, endDate });
        } else {
            alert('시작 날짜와 종료 날짜를 모두 선택해주세요.');
        }
    };

    return {
        dashboardData,
        loading,
        startDate,
        endDate,
        playerName,
        setStartDate,
        setEndDate,
        handleSearch,
        fetchPatientRecordData
    };
};