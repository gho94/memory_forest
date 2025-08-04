import React, { useState } from 'react';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';

import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';

function PatientProfilePage() {
  const [showAlarmModal, setShowAlarmModal] = useState(false);

  return (
    <div className="app-container d-flex flex-column">
      <FamilyHeader />
      
      <button
        type="button"
        className="alarm"
        aria-label="알림 열기"
        onClick={() => setShowAlarmModal(true)}
        style={{ 
          position: 'fixed', 
          top: '1rem', 
          right: '1rem', 
          width: '40px', 
          height: '40px', 
          background: 'none', 
          border: 'none', 
          cursor: 'pointer',
          zIndex: 1000
        }}
      />

      <main className="content-area guardian-con">
        <div className="menu-title">
          <div>기록자 추가</div>
          <div></div>
        </div>

        <form className="signup-form patient-signup-form">
          <div className="profile-upload-con">
            <div className="profile-upload">
              <input type="file" id="fileInput" accept="image/*" />
              <label htmlFor="fileInput" className="upload-label" id="previewBox">
                <i className="bi bi-person"></i>
              </label>
            </div>
          </div>

          <div className="form-control-con">
            <input type="text" className="form-control" placeholder="이름" />
          </div>

          <div className="form-control-con">
            <input type="date" className="form-control" placeholder="생년월일" />
            <i className="bi bi-calendar calendar-icon"></i>
          </div>

          <div className="form-control-con">
            <select className="form-control" placeholder="성별" defaultValue="">
              <option disabled hidden value="">
                성별
              </option>
              <option value="m">남성</option>
              <option value="w">여성</option>
            </select>
          </div>

          <div className="form-control-con">
            <select className="form-control" placeholder="관계" defaultValue="">
              <option disabled hidden value="">
                관계
              </option>
              <option value="parent">부모</option>
              <option value="spouse">배우자</option>
              <option value="sibling">형제자매</option>
              <option value="child">자녀</option>
              <option value="grandchild">손자/손녀</option>
              <option value="relative">기타 친척</option>
              <option value="friend">친구</option>
              <option value="neighbor">이웃</option>
              <option value="caregiver">요양보호사</option>
              <option value="etc">기타</option>
            </select>
          </div>

          <button type="submit" className="btn btn-login">
            등록하기
          </button>
        </form>
      </main>

      {/* 알람 모달 */}
      {showAlarmModal && (
        <div className="alarm-modal-overlay">
          <div className="position-relative custom-modal">
            <button
              type="button"
              className="custom-close"
              aria-label="모달 닫기"
              onClick={() => setShowAlarmModal(false)}
              style={{ background: 'none', border: 'none', fontSize: '2rem', cursor: 'pointer' }}
            >
              &times;
            </button>

            <div className="text-center mb-3">
              <div className="center-group">
                <div className="logo" aria-label="기억 숲 로고"></div>
                <div className="title">알림</div>
              </div>
            </div>

            <div className="modal-body-scroll d-flex flex-column gap-3">
              <div className="alert-card active d-flex align-items-start gap-2">
                <div className="profile-img" alt="avatar" />
                <div>
                  <div className="patient-con">
                    <span className="patient-name">환자01</span>
                    <span className="patient-reg-date">2025.06.20 15:20</span>
                  </div>
                  <div className="alarm-content">
                    오늘의 게임을 완료하였습니다.
                    <br />
                    지금 바로 결과를 확인해보세요.
                  </div>
                </div>
              </div>

              <div className="alert-card inactive d-flex align-items-start gap-2">
                <div className="profile-img" alt="avatar" />
                <div>
                  <div className="patient-con">
                    <span className="patient-name">환자01</span>
                    <span className="patient-reg-date">2025.06.20 15:20</span>
                  </div>
                  <div className="alarm-content">
                    오늘의 게임을 완료하였습니다.
                    <br />
                    지금 바로 결과를 확인해보세요.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <FamilyFooter />
    </div>
  );
}

export default PatientProfilePage;
