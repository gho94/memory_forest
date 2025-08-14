import React from 'react';
import StatSkeleton from '@/components/skeleton/PatientDetailStatSkeleton';

const RecordStatItem = ({ stats, loading }) => {
    return (
        <div className="patient-activity-con row">
            <div className="col-6">
                오늘 : {loading ? <StatSkeleton /> : <><span>{stats?.todayScore}</span>점</>}
            </div>
            <div className="col-6">
                이번주 참여율 : {loading ? <StatSkeleton /> : <><span>{stats?.weeklyParticipation}</span>%</>}
            </div>
            <div className="col-6">
                어제 : {loading ? <StatSkeleton /> : <><span>{stats?.yesterdayScore}</span>점</>}
            </div>
            <div className="col-6">
                전체 평균점수 : {loading ? <StatSkeleton /> : <><span>{stats?.overallScore}</span>점</>}
            </div>
            <div className="col-6">
                일주일 평균점수 : {loading ? <StatSkeleton /> : <><span>{stats?.weeklyScore}</span>점</>}
            </div>
            <div className="col-6">
                주간 평균점수 : {loading ? <StatSkeleton /> : <><span>{stats?.weeklyScoreDiff > 0 ? '+' : ( stats?.weeklyScoreDiff === 0 ? '' : '-')}{stats?.weeklyScoreDiff}</span>점</>}
            </div>
        </div>
    );
};

export default RecordStatItem;