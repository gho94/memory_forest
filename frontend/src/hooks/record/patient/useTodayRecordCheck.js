import { useState, useCallback } from 'react';

const useTodayRecordCheck = () => {
    const [todayRecordExists, setTodayRecordExists] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    const checkTodayRecord = useCallback(async () => {
        setIsLoading(true);
        try {
            const response = await fetch(`${window.API_BASE_URL}/recorder/record/today-exists`,{
                credentials: 'include'
            });
            const data = await response.json();
            setTodayRecordExists(data.exists);
            setIsLoading(false);
            return data.exists;
        } catch (error) {
            console.error('오늘 기록 확인 실패:', error);
            setTodayRecordExists(false);
            setIsLoading(false);
            return false;
        }
    }, []);

    return {
        todayRecordExists,
        isLoading,
        checkTodayRecord
    };
};

export default useTodayRecordCheck;