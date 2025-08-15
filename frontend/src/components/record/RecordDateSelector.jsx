import React from 'react';

const RecordDateSelector = ({
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
                      }) => {
    return (
        <div className="date-selector-container d-flex justify-content-center gap-3 mb-1">
            {/* Year Dropdown */}
            <div className="record-dropdown-wrapper year-dropdown">
                <button
                    className="record-dropdown-display"
                    onClick={() => setIsYearOpen(!isYearOpen)}
                >
                    {selectedYear}
                </button>
                {isYearOpen && (
                    <ul className="record-dropdown-options">
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
            <div className="record-dropdown-wrapper month-dropdown">
                <button
                    className="record-dropdown-display"
                    onClick={() => {
                        setIsMonthOpen(!isMonthOpen);
                    }}
                >
                    {selectedMonth.toString().padStart(2, '0')}
                </button>
                {isMonthOpen && (
                    <ul className="record-dropdown-options">
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
    );
};

export default RecordDateSelector;