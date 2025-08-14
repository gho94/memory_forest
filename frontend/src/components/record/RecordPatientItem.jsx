import React from 'react';

const RecordPatientItem = ({ record, isExpanded, onItemClick }) => {
    const formatDuration = (seconds) => {
        if (!seconds) return '0:00';
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    };

    return (
        <div className="record-item mb-3">
            <div
                className="record-header p-3"
                onClick={() => onItemClick(record.id)}
                style={{cursor: 'pointer'}}
            >
                <div className="d-flex align-items-center justify-content-between flex-wrap">
                    <div className="d-flex align-items-center">
                        <button className="btn play-btn">
                            {isExpanded ? '▼' : '▶'}
                        </button>
                        <span className="record-date">{record.day}일</span>
                        {record.audioUrl && (
                            <audio
                                controls
                                className="ms-2"
                                style={{width: '209px', height: '38px'}}
                                preload="metadata"
                            >
                                <source src={record.audioUrl} type="audio/wav"/>
                                브라우저가 오디오를 지원하지 않습니다.
                            </audio>
                        )}

                        {record.hasAudio && !record.audioUrl && (
                            <span className="ms-2 text-muted">음성 로딩 중...</span>
                        )}
                    </div>
                </div>

                {isExpanded && record.content && (
                    <div className="record-content col-12">
                        <p className="record-text">{record.content}</p>
                        <div className="audio-controls-expanded d-flex align-items-center justify-content-center mt-3">
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default RecordPatientItem;