import React from 'react';
import RecordPatientItem from '@/components/record/RecordPatientItem';

const RecordPatientList = ({ records, expandedItem, onItemClick, loading, error }) => {
    if (loading) {
        return (
            <div className="records-list text-center py-4">
                <div className="spin-con">
                    <div className="spin"></div>
                    <div className="spin-desc">
                        기록 준비 중...
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="records-list text-center py-4">
                <div className="alert alert-danger" role="alert">
                    {error}
                </div>
            </div>
        );
    }

    if (records.length === 0) {
        return (
            <div className="records-list text-center py-4">
                <p className="record-nodata">선택한 기간에 기록이 없습니다.</p>
            </div>
        );
    }

    return (
        <div className="records-list">
            {records.map((record) => (
                <RecordPatientItem
                    key={record.id}
                    record={record}
                    isExpanded={expandedItem === record.id}
                    onItemClick={onItemClick}
                />
            ))}
        </div>
    );
};

export default RecordPatientList;