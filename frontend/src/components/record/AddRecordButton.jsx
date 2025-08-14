import React from 'react';
import { Link } from 'react-router-dom';
const AddRecordButton = ({ disabled }) => {
    if (disabled) {
        return (
            <div className="add-record-container text-center mt-4 mb-4">
                <button
                    className="btn btn-patient disabled"
                    disabled={disabled}
                >
                    기록 추가하기
                </button>
            </div>
        );
    }

    return (
        <div className="add-record-container text-center mt-4 mb-4">
            <Link
                to="/recorder/record/create"
                className="btn btn-patient"
            >
                기록 추가하기
            </Link>
        </div>
    );
};

export default AddRecordButton;