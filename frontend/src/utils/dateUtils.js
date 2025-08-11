export const dateUtils = {
    parseSearchDate: (searchDateStr) => {
        if (!searchDateStr) return null;
        const match = searchDateStr.match(/(\d{4})년 (\d{2})월 (\d{2})일/);
        if (match) {
            const [, year, month, day] = match;
            return `${year}-${month}-${day}`;
        }
        return null;
    },
    getWeekStartDate: (endDate) => {
        const endDateObj = new Date(endDate);
        const startDateObj = new Date(endDateObj);
        startDateObj.setDate(endDateObj.getDate() - 6);
        return startDateObj.toISOString().split('T')[0];
    }
};