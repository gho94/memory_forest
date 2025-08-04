import React from 'react';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';

import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';

function PatientDetailPage() {
  return (
    <div className="app-container d-flex flex-column">
      <FamilyHeader />

      <main className="content-area guardian-con">
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

      {/* 알람 모달 */}
      <input type="checkbox" id="toggle-alarm-modal" />
      <div className="modal-overlay alarm-modal-overlay">
        <div className="position-relative custom-modal">
          <label htmlFor="toggle-alarm-modal" className="custom-close">&times;</label>
          <div className="text-center mb-3">
            <div className="center-group">
              <div className="logo" aria-label="기억 숲 로고"></div>
              <div className="title">알림</div>
            </div>
          </div>

          <div className="modal-body-scroll d-flex flex-column gap-3">
            <div className="alert-card active d-flex align-items-start gap-2">
              <div className="profile-img" alt="avatar"></div>
              <div>
                <div className="patient-con">
                  <span className="patient-name">환자01</span>
                  <span className="patient-reg-date">2025.06.20 15:20</span>
                </div>
                <div className="alarm-content">
                  오늘의 게임을 완료하였습니다.<br />지금 바로 결과를 확인해보세요.
                </div>
              </div>
            </div>

            <div className="alert-card inactive d-flex align-items-start gap-2">
              <div className="profile-img" alt="avatar"></div>
              <div>
                <div className="patient-con">
                  <span className="patient-name">환자01</span>
                  <span className="patient-reg-date">2025.06.20 15:20</span>
                </div>
                <div className="alarm-content">
                  오늘의 게임을 완료하였습니다.<br />지금 바로 결과를 확인해보세요.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <FamilyFooter />
    </div>
  );
}

export default PatientDetailPage;
