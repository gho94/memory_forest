import React from 'react';

const GamePlayerDatePickerItem = ({ startDate, endDate, setStartDate, setEndDate, handleSearch }) => {
    return (
        <div className="date-picker-wrapper">
            <label className="date-input readonly">
                <input
                    type="date"
                    name="startDate"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                />
            </label>
            <span className="range-symbol">~</span>
            <label className="date-input">
                <input
                    type="date"
                    name="endDate"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                />
            </label>
            <div className="search-btn" onClick={handleSearch}></div>
        </div>
    );
};

export default GamePlayerDatePickerItem;