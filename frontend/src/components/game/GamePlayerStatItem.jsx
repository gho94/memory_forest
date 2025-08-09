import React from 'react';
import StatSkeleton from '@/components/skeleton/PatientDetailStatSkeleton';

const GamePlayerStatItem = ({ stats, loading }) => {
    return (
        <div className="patient-activity-con row">
            <div className="col-6">
                오늘 : {loading ? <StatSkeleton /> : <><span>{stats?.todayScore}</span>점 (<span>{stats?.todayAccuracy}</span>%)</>}
            </div>
            <div className="col-6">
                이번주 참여율 : {loading ? <StatSkeleton /> : <><span>{stats?.weeklyParticipation}</span>%</>}
            </div>
            <div className="col-6">
                어제 : {loading ? <StatSkeleton /> : <><span>{stats?.yesterdayScore}</span>점 (<span>{stats?.yesterdayAccuracy}</span>%)</>}
            </div>
            <div className="col-6">
                전체 정답률 : {loading ? <StatSkeleton /> : <><span>{stats?.overallAccuracy}</span>%</>}
            </div>
            <div className="col-6">
                일주일 정답률 : {loading ? <StatSkeleton /> : <><span>{stats?.weeklyAccuracy}</span>%</>}
            </div>
            <div className="col-6">
                주간 정답률 : {loading ? <StatSkeleton /> : <><span>{stats?.weeklyAccuracyDiff > 0 ? '+' : ''}{stats?.weeklyAccuracyDiff}</span>%</>}
            </div>
        </div>
    );
};

export default GamePlayerStatItem;