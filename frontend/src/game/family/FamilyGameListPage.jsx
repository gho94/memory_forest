import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';
import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';
import AlarmModal from '@/components/modal/AlarmModal';

function FamilyGameListPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [gameId, setGameId] = useState(null);
  const [gameName, setGameName] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [gameDetails, setGameDetails] = useState([]);
  const [fileUrls, setFileUrls] = useState({});

  useEffect(() => {
    if (location.state && location.state.gameId) {
      setGameId(location.state.gameId);
      setGameName(location.state.gameName);
      console.log('받은 gameId:', location.state.gameId);
      console.log('받은 gameName:', location.state.gameName);
    }
  }, [location.state]);

  const handleGoToList = () => {
    navigate('/companion/dashboard', { 
      state: { isGame: true } 
    });
  };

  // 파일 ID로 이미지 URL 조회
  const fetchFileUrl = async (fileId) => {
    if (!fileId) return null;
    
    try {
      const response = await fetch(`http://localhost:8080/api/files/${fileId}`);
      if (!response.ok) {
        console.error('파일 조회 실패:', fileId);
        return null;
      }
      const fileData = await response.json();
      return fileData.fileUrl;
    } catch (error) {
      console.error('파일 URL 조회 오류:', error);
      return null;
    }
  };

  // 게임 상세 정보와 함께 이미지 URL도 조회
  const fetchGameDetail = async () => {
    if (!gameId) return;
    
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8080/companion/games/list?gameId=${gameId}`);
      if (!response.ok) {
        throw new Error('데이터를 가져오는데 실패했습니다.');
      }
      const data = await response.json();
      console.log('받아온 게임 데이터:', data);
      setGameDetails(data);
      
      // 각 게임 상세 정보의 fileId로 이미지 URL 조회
      const urlPromises = data.map(async (gameDetail) => {
        if (gameDetail.fileId) {
          const fileUrl = await fetchFileUrl(gameDetail.fileId);
          return { gameSeq: gameDetail.gameSeq, fileUrl };
        }
        return { gameSeq: gameDetail.gameSeq, fileUrl: null };
      });
      
      const urlResults = await Promise.all(urlPromises);
      const urlMap = {};
      urlResults.forEach(result => {
        if (result.fileUrl) {
          urlMap[result.gameSeq] = result.fileUrl;
        }
      });
      
      setFileUrls(urlMap);
      setError(null);
    } catch (err) {
      console.error('게임 데이터 가져오기 실패:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGameDetail();
  }, [gameId]);

  return (
    <div className="app-container d-flex flex-column">
      <FamilyHeader />

      <main className="content-area guardian-con">
        <div className="menu-title">
          <div>{gameName}</div>
        </div>

        <div className="game-list-wrap">
          <div className="game-list-con">
            {gameDetails.map((gameDetail) => (
              <div className="game-item" key={gameDetail.gameSeq}>
                <div className="game-number">{gameDetail.gameSeq}</div>
                <div className="game-box">
                  <div className="game-img">
                    <img src={fileUrls[gameDetail.gameSeq]} alt="문제 이미지" height="100%" width="100%" />
                  </div>
                  <div className="game-texts">
                    <div className="game-title">{gameDetail.description}</div>
                    <div className="game-answer">정답 : {gameDetail.answerText}</div>
                  </div>
                  <button className="game-edit-btn">수정</button>
                </div>
              </div>
            ))}
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
}

export default FamilyGameListPage;
