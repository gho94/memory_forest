import React from 'react';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';

import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';

function FamilyGameCreatePage() {
  return (
    <div className="app-container d-flex flex-column">
      <FamilyHeader />

      <main className="content-area family-con">
        <div className="menu-title">
          <div>게임 만들기</div>
          <div className="progress">
            <div
              className="progress-bar"
              role="progressbar"
              style={{ width: '60%' }}
              aria-valuenow="6"
              aria-valuemin="0"
              aria-valuemax="10"
            ></div>
            <div className="progress-label">6 / 10</div>
          </div>
        </div>

        <form className="signup-form game-signup-form">
          <div className="form-control-con">
            <input
              type="text"
              className="form-control"
              placeholder="게임 제목을 입력하세요."
            />
          </div>

          <div className="form-control-con">
            <div className="form-control game-file-desc-con">
              <div className="game-file-desc mb-3 mt-2">
                게임에 사용할 사진을 업로드하세요.
              </div>
              <button className="btn btn-add" type="button">파일 선택</button>
            </div>
          </div>

          <div className="form-control-con">
            <input
              type="text"
              className="form-control"
              placeholder="정답 단어를 입력하세요."
            />
          </div>

          <div className="form-control-con">
            <textarea
              className="form-control"
              placeholder="설명을 입력하세요."
            ></textarea>
          </div>

          <button type="button" className="btn btn-login">
            다음 문제 추가하기
          </button>
          <button type="submit" className="btn btn-login">
            게임 생성완료
          </button>
        </form>
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

export default FamilyGameCreatePage;
