import React from 'react';

const PatientDetailChartSkeleton = () => (
    <div style={{
        borderRadius: '8px',
        height: '300px',
        width: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#999',
        fontSize: '14px'
    }}>
        차트 로딩 중...
    </div>
);

export default PatientDetailChartSkeleton;
