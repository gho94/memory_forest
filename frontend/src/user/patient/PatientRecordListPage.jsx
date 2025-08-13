import '@/assets/css/common.css';
import '@/assets/css/patient.css';
import PatientHeader from "@/components/layout/header/PatientHeader";
import PatientFooter from "@/components/layout/footer/PatientFooter";
import React from 'react';
import { useDateSelector } from '@/hooks/record/patient/useDateSelector';
import { useRecordsLogic } from '@/hooks/record/patient/useRecordsLogic';
import RecordDateSelector from '@/components/record/RecordDateSelector';
import RecordPatientList from '@/components/record/RecordPatientList';
import AddRecordButton from '@/components/record/AddRecordButton';

const PatientRecordListPage = () => {
    const {
        selectedYear,
        selectedMonth,
        isYearOpen,
        isMonthOpen,
        years,
        months,
        setIsYearOpen,
        setIsMonthOpen,
        handleYearSelect,
        handleMonthSelect
    } = useDateSelector();

    const {
        records,
        expandedItem,
        loading,
        error,
        todayRecordExists,
        handleItemClick,
        checkTodayRecord
    } = useRecordsLogic(selectedYear, selectedMonth);

    return (
        <div className="app-container d-flex flex-column">
            <PatientHeader/>

            <main className="content-area patient-con record-result-area">
                <div className="greeting">나의 진행도</div>

                <RecordDateSelector
                    selectedYear={selectedYear}
                    selectedMonth={selectedMonth}
                    isYearOpen={isYearOpen}
                    isMonthOpen={isMonthOpen}
                    years={years}
                    months={months}
                    setIsYearOpen={setIsYearOpen}
                    setIsMonthOpen={setIsMonthOpen}
                    handleYearSelect={handleYearSelect}
                    handleMonthSelect={handleMonthSelect}
                />

                <RecordPatientList
                    records={records}
                    expandedItem={expandedItem}
                    onItemClick={handleItemClick}
                    loading={loading}
                    error={error}
                />

                <AddRecordButton
                    disabled={todayRecordExists}
                />
            </main>

            <PatientFooter/>
        </div>
    );
};

export default PatientRecordListPage;