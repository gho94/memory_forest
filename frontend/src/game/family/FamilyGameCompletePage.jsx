import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';
import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';
// import AlarmModal from '@/components/modal/AlarmModal';

function FamilyGameCompletePage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { gameData } = location.state || {};
  console.log('gameData:', gameData);
  const gameTitle = gameData.gameName || 'untitled';
  const totalProblems = gameData.totalProblems || 0;

    const gameId = gameData.gameId;
    const [isSharing, setIsSharing] = useState(false);

  const handleGoToList = () => {
    navigate('/companion/dashboard');
  };

    const handleLinkCopy = async () => {
        if (isSharing) return;

        const shareUrl = await generateShareUrl();
        if (!shareUrl) return;

        try {
            await navigator.clipboard.writeText(shareUrl);
            alert('링크가 복사되었습니다!');
        } catch (error) {
            // 복사 실패 시 대체 방법
            const textArea = document.createElement('textarea');
            textArea.value = shareUrl;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            alert('링크가 복사되었습니다!');
        }
    };

    const generateShareUrl = async () => {
        if (isSharing) return null;

        setIsSharing(true);

        try {
            // 게임과 연결된 환자 ID 사용 (기존 API 재활용)
            const patientId = gameData.players?.[0]?.userId || gameData.patientId;

            if (!patientId) {
                alert('공유할 수 있는 정보가 없습니다.');
                return null;
            }

            console.log('공유 링크 생성 시작 - 환자ID:', patientId);

            const response = await fetch(`${window.API_BASE_URL}/api/recorder/${patientId}/share`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });

            const data = await response.json();
            console.log('서버 응답:', data);

            if (data.success) {
                console.log('공유 링크 생성 성공:', data.shareUrl);
                return data.shareUrl;
            } else {
                alert(data.message || '공유 링크 생성에 실패했습니다.');
                return null;
            }
        } catch (error) {
            console.error('공유 링크 생성 실패:', error);
            alert('공유 링크 생성에 실패했습니다. 네트워크를 확인해주세요.');
            return null;
        } finally {
            setIsSharing(false);
        }
    };


 return (
    <div className="app-container d-flex flex-column">
      <FamilyHeader />

      <main className="content-area guardian-con center">
        <div className="game-result-title">게임 생성 완료!</div>

        <div className="signup-form game-signup-form game-complete-gap">
          <div className="row game-result-con">
            <div className="col-5 desc-title">게임 제목</div>
            <div className="col-7">{gameTitle}</div>
            <div className="col-5 desc-title">문제 개수</div>
            <div className="col-7">{totalProblems}</div>
          </div>

          <div>
            <div className="game-result-share-text">게임 공유하기</div>
            <div className="game-result-share-icon mt-3 row">
              <div className="col-6 kakaotalk-icon"></div>
              <div className="col-6 link-icon" onClick={async () => {const patientId = gameData.selectedPatients?.[0];
                  if (!patientId) {alert('환자 ID 없음');
                      return;
                  } try {
                      const response = await fetch(`${window.API_BASE_URL}/api/recorder/${patientId}/share`, {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          credentials: 'include'
                      });
                      const data = await response.json();
                      if (data.success) {
                          await navigator.clipboard.writeText(data.shareUrl);
                          alert('링크 복사 완료');
                      } else {
                          alert('API 실패: ' + data.message);
                      }
                  } catch (error) {
                      alert('오류: ' + error.message);
                  }
              }}
              ></div>



            </div>
          </div>
          <button type="button" className="btn btn-login" onClick={handleGoToList}>목록으로</button>
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
