import { useState, useEffect } from 'react';
import useFileUrl from '@/hooks/common/useFileUrl';
import useTodayRecordCheck from "@/hooks/record/patient/useTodayRecordCheck";

export const useRecordsLogic = (selectedYear, selectedMonth) => {
    const [expandedItem, setExpandedItem] = useState(null);
    const [records, setRecords] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const { fetchFileUrl, isLoading: fileUrlLoading } = useFileUrl();
    const { todayRecordExists, checkTodayRecord } = useTodayRecordCheck();

    // API에서 기록 데이터 가져오기
    const fetchRecords = async () => {
        setLoading(true);
        setError(null);

        try {
            // URL에 쿼리 파라미터로 년도와 월 추가
            const params = new URLSearchParams({
                year: selectedYear.toString(),
                month: selectedMonth.toString()
            });

            const response = await fetch(`${window.API_BASE_URL}/recorder/record/list?${params.toString()}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error('기록을 불러오는데 실패했습니다.');
            }

            const data = await response.json();

            // API 응답 데이터를 UI에서 사용할 형태로 변환
            const formattedRecords = await Promise.all(
                data.map(async (record) => {
                    let audioUrl = null;

                    // file_id가 있으면 파일 URL 가져오기
                    if (record.fileId) {
                        try {
                            audioUrl = await fetchFileUrl(record.fileId);
                        } catch (urlError) {
                            console.error('파일 URL 가져오기 실패:', urlError);
                        }
                    }

                    // 날짜에서 일(day)만 추출 (API 응답에 날짜 필드가 있다고 가정)
                    const recordDate = new Date(record.createdAt || Date.now());
                    const day = recordDate.getDate().toString().padStart(2, '0');

                    return {
                        id: record.recordId,
                        day: day,
                        content: record.text || '',
                        duration: record.duration || 0,
                        hasAudio: !!record.file_id,
                        audioUrl: audioUrl,
                        file_id: record.file_id
                    };
                })
            );

            setRecords(formattedRecords);
        } catch (err) {
            setError(err.message);
            console.error('기록 불러오기 오류:', err);
        } finally {
            setLoading(false);
        }
    };

    // 선택된 년/월이 변경될 때마다 데이터 다시 가져오기
    useEffect(() => {
        fetchRecords();
    }, [selectedYear, selectedMonth]);

    useEffect(() => {
        checkTodayRecord();
    }, []);

    const handleItemClick = (itemId) => {
        setExpandedItem(expandedItem === itemId ? null : itemId);
    };


    return {
        records,
        expandedItem,
        loading,
        error,
        todayRecordExists, // state 반환
        handleItemClick,
        checkTodayRecord,
        fetchRecords
    };
};