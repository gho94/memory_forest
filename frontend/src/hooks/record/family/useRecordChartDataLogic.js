import { dateUtils } from '@/utils/dateUtils';

export const useRecordChartDataLogic = (dashboardData) => {
    const generateChartData = () => {
        console.log(dashboardData);

        if (!dashboardData?.weeklyChart || !dashboardData?.searchDate) {
            return { categories: [], data: [] };
        }

        const searchDateStr = dateUtils.parseSearchDate(dashboardData.searchDate);
        const baseDate = new Date(searchDateStr);
        baseDate.setHours(0, 0, 0, 0);

        // 7일간의 날짜 배열 생성
        const dates = Array.from({ length: 7 }, (_, i) => {
            const date = new Date(baseDate);
            date.setDate(baseDate.getDate() - (6 - i));
            return date;
        });

        // 날짜별 기록 수 매핑 (게임은 accuracy, 기록은 count)
        const chartDataMap = dashboardData.weeklyChart.reduce((acc, item) => {
            acc[item.date] = parseInt(item.score || 0);
            return acc;
        }, {});

        // 카테고리와 데이터 생성
        const categories = dates.map(date => {
            const dayNames = ['일', '월', '화', '수', '목', '금', '토'];
            const dayOfWeek = dayNames[date.getDay()];
            return `${date.getFullYear().toString().slice(2)}.${(date.getMonth() + 1).toString().padStart(2, '0')}.${date.getDate().toString().padStart(2, '0')}(${dayOfWeek})`;
        });

        const data = dates.map(date => {
            const dateStr = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
            return chartDataMap[dateStr] || 0;
        });

        return { categories, data };
    };

    return generateChartData();
};