import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';
import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';
// import AlarmModal from '@/components/modal/AlarmModal';

function FamilyGameCompletePage() {
 return (
    <div className="app-container d-flex flex-column">
      <FamilyHeader />

      <main className="content-area guardian-con center">
        <div className="game-result-title">게임 생성 완료!</div>

        <div className="signup-form game-signup-form game-complete-gap">
          <div className="row game-result-con">
            <div className="col-5 desc-title">게임 제목</div>
            <div className="col-7">untitled10</div>
            <div className="col-5 desc-title">문제 개수</div>
            <div className="col-7">10</div>
          </div>

          <div>
            <div className="game-result-share-text">게임 공유하기</div>
            <div className="game-result-share-icon mt-3 row">
              <div className="col-6 kakaotalk-icon"></div>
              <div className="col-6 link-icon"></div>
            </div>
          </div>
          <button type="button" className="btn btn-login">목록으로</button>
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
};


export default FamilyGameCompletePage;
