import '@/assets/css/common.css';
import '@/assets/css/patient.css';
import PatientHeader from "@/components/layout/header/PatientHeader";
import PatientFooter from "@/components/layout/footer/PatientFooter";
import React, {useState, useEffect} from 'react';

const PatientRecordListPage = () => {
    const [selectedYear, setSelectedYear] = useState(2025);
    const [selectedMonth, setSelectedMonth] = useState(8);
    const [isYearOpen, setIsYearOpen] = useState(false);
    const [isMonthOpen, setIsMonthOpen] = useState(false);
    const [expandedItem, setExpandedItem] = useState(null);
    const [records, setRecords] = useState([
        {id: 1, day: '27', content: "오늘은 밤을 먹었다. 잠 잤다. 산책을 했는데 나무를 봤다", hasAudio: true},
        {id: 2, day: '24', content: "123", hasAudio: true},
        {id: 3, day: '08', content: "456", hasAudio: true}
    ]);

    const currentYear = new Date().getFullYear();
    const currentMonth = new Date().getMonth() + 1;
    const currentDay = new Date().getDate();

    // 년도/월 범위 생성 (2024년부터 현재 년도까지만)
    const years = Array.from({length: currentYear - 2024 + 1}, (_, i) => 2024 + i);
    const months = Array.from({length: 12}, (_, i) => i + 1);

    // 미래 날짜 검증
    const isFutureDate = (year, month) => {
        if (year === currentYear && month > currentMonth || year > currentYear){
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

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (!event.target.closest('.year-dropdown')) {
                setIsYearOpen(false);
            }
            if (!event.target.closest('.month-dropdown')) {
                setIsMonthOpen(false);
            }
        };

        document.addEventListener('click', handleClickOutside);
        return () => {
            document.removeEventListener('click', handleClickOutside);
        };
    }, []);

    const handleMonthSelect = (month) => {
        handleDateChange(selectedYear, month);
        setIsMonthOpen(false);
    };
    const handleItemClick = (itemId) => {
        setExpandedItem(expandedItem === itemId ? null : itemId);
    };

    // 오늘 날짜 기록 존재 확인
    const hasTodayRecord = () => {
        if (selectedYear !== currentYear || selectedMonth !== currentMonth) return false;
        return records.some(record => record.day === currentDay);
    };

    return (
        <div className="app-container d-flex flex-column">
            <PatientHeader/>

            <main className="content-area patient-con record-result-area">
                <div className="greeting">나의 진행도</div>

                {/* Date Selector */}
                <div className="date-selector-container d-flex justify-content-center gap-3 mb-1">
                    {/* Year Dropdown */}
                    <div className="custom-dropdown-wrapper year-dropdown">
                        <button
                            className="custom-dropdown-display"
                            onClick={() => setIsYearOpen(!isYearOpen)}
                        >
                            {selectedYear}
                        </button>
                        {isYearOpen && (
                            <ul className="custom-dropdown-options">
                                {years.map(year => (
                                    <li
                                        key={year}
                                        onClick={() => handleYearSelect(year)}
                                        className={selectedYear === year ? 'selected' : ''}
                                    >
                                        {year}
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                    <span className="date-label align-self-center">년</span>

                    {/* Month Dropdown */}
                    <div className="custom-dropdown-wrapper month-dropdown">
                        <button
                            className="custom-dropdown-display"
                            onClick={() => setIsMonthOpen(!isMonthOpen)}
                        >
                            {selectedMonth.toString().padStart(2, '0')}
                        </button>
                        {isMonthOpen && (
                            <ul className="custom-dropdown-options">
                                {months.map(month => (
                                    <li
                                        key={month}
                                        onClick={() => handleMonthSelect(month)}
                                        className={selectedMonth === month ? 'selected' : ''}
                                    >
                                        {month.toString().padStart(2, '0')}
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                    <span className="date-label align-self-center">월</span>
                </div>

                {/* Records List */}
                <div className="records-list">
                    {records.map((record) => (
                        <div key={record.id} className="record-item mb-3">
                            <div
                                className="record-header p-3"
                                onClick={() => handleItemClick(record.id)}
                                style={{cursor: 'pointer'}}
                            >
                                <div className="d-flex align-items-center justify-content-between flex-wrap">

                                    <div className="d-flex align-items-center">
                                        <button className="btn play-btn">
                                            {expandedItem === record.id ? '▼' : '▶'}
                                        </button>
                                        <span className="record-date">{record.day}일</span>

                                        <audio
                                            controls
                                            className="ms-2"
                                            style={{width: '209px', height: '38px'}}
                                        >
                                            <source src="#" type="audio/mpeg"/>
                                            브라우저가 오디오를 지원하지 않습니다.
                                        </audio>
                                    </div>

                                </div>
                                {expandedItem === record.id && record.content && (
                                    <div className="record-content col-12">
                                        <p className="record-text">{record.content}</p>

                                        <div
                                            className="audio-controls-expanded d-flex align-items-center justify-content-center mt-3">
                                        </div>
                                    </div>
                                )}
                            </div>


                        </div>
                    ))}
                </div>

                {/* Add Record Button */}
                <div className="add-record-container text-center mt-4 mb-4">
                    <button
                        className={`btn btn-patient ${hasTodayRecord() ? 'disabled' : ''}`}
                        disabled={hasTodayRecord()}
                    >
                        기록 추가하기
                    </button>
                </div>
            </main>

            <PatientFooter/>
        </div>
    );
};

export default PatientRecordListPage;