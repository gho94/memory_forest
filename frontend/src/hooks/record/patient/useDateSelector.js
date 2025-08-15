import { useState, useEffect } from 'react';

export const useDateSelector = () => {
    const [selectedYear, setSelectedYear] = useState(2025);
    const [selectedMonth, setSelectedMonth] = useState(8);
    const [isYearOpen, setIsYearOpen] = useState(false);
    const [isMonthOpen, setIsMonthOpen] = useState(false);

    const currentYear = new Date().getFullYear();
    const currentMonth = new Date().getMonth() + 1;

    // 년도/월 범위 생성 (2024년부터 현재 년도까지만)
    const years = Array.from({length: currentYear - 2024 + 1}, (_, i) => 2024 + i);
    const months = Array.from({length: 12}, (_, i) => i + 1);

    // 미래 날짜 검증
    const isFutureDate = (year, month) => {
        if (year === currentYear && month > currentMonth || year > currentYear) {
            alert("미래의 날짜를 선택할 수 없습니다.");
            return true;
        }
        return false;
    };

    // 날짜 변경 핸들러
    const handleDateChange = (newYear, newMonth) => {
        if (isFutureDate(newYear, newMonth)) {
            // 미래 날짜 선택 시 현재 날짜로 리셋
            setSelectedYear(currentYear);
            setSelectedMonth(currentMonth);
            return;
        }
        setSelectedYear(newYear);
        setSelectedMonth(newMonth);
    };

    // 드롭다운 핸들러
    const handleYearSelect = (year) => {
        handleDateChange(year, selectedMonth);
        setIsYearOpen(false);
    };

    const handleMonthSelect = (month) => {
        handleDateChange(selectedYear, month);
        setIsMonthOpen(false);
    };

    // 드롭다운 외부 클릭 처리
    useEffect(() => {
        const handleClickOutside = (event) => {

            // 클릭된 요소가 년도 드롭다운 내부가 아니면 닫기
            if (!event.target.closest('.year-dropdown') && isYearOpen) {
                setIsYearOpen(false);
            }

            // 클릭된 요소가 월 드롭다운 내부가 아니면 닫기
            if (!event.target.closest('.month-dropdown') && isMonthOpen) {
                setIsMonthOpen(false);
            }
        };

        // mousedown 이벤트를 사용해서 클릭 이벤트보다 먼저 처리
        if (isYearOpen || isMonthOpen) {
            const timeoutId = setTimeout(() => {
                document.addEventListener('mousedown', handleClickOutside);
            }, 10);

            return () => {
                clearTimeout(timeoutId);
                document.removeEventListener('mousedown', handleClickOutside);
            };
        }
    }, [isYearOpen, isMonthOpen]);

    return {
        selectedYear,
        selectedMonth,
        isYearOpen,
        isMonthOpen,
        years,
        months,
        currentYear,
        currentMonth,
        setIsYearOpen,
        setIsMonthOpen,
        handleYearSelect,
        handleMonthSelect
    };
};