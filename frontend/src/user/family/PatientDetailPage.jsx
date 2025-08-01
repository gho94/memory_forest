
import React from 'react';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';

import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';
import AlarmModal from '@/components/modal/AlarmModal';

function PatientDetailPage() {
  return (
    <div className="app-container d-flex flex-column">
      <FamilyHeader />

      <main className="content-area family-con">
        <div className="detail-title">
          <div><span>환자 01</span> 최근 활동</div>
          <div>
            <div className="icon-btn print-btn"></div>
            <div className="icon-btn trash-btn"></div>
          </div>
        </div>

        <div className="patient-activity-con row">
          <div className="col-6">오늘 : <span>76</span>점</div>
          <div className="col-6">이번주 참여율 : <span>85</span>%</div>
          <div className="col-6">어제 : <span>91</span>점</div>
          <div className="col-6">점수 향상률 : <span>+7</span>%</div>
          <div className="col-6">일주일 평균 : <span>81.23</span>점</div>
          <div className="col-6">평균 위험도 : <span>46</span>%</div>
        </div>

        <div className="date-picker-wrapper">
          <label className="date-input">
            <input type="date" />
          </label>
          <span className="range-symbol">~</span>
          <label className="date-input">
            <input type="date" />
          </label>
          <div className="search-btn"></div>
        </div>

        <div className="chart-con">
          <div></div>
          <div></div>
        </div>
      </main>

      <AlarmModal />
      <FamilyFooter />
    </div>
  );
}

export default PatientDetailPage;
