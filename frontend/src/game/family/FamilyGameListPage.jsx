import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';
import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';
import useFileUrl from '@/hooks/common/useFileUrl';
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
  const { fetchFileUrl, isLoading } = useFileUrl();

  useEffect(() => {
    if (location.state && location.state.gameId) {
      setGameId(location.state.gameId);
      setGameName(location.state.gameName);
      console.log('받은 gameId:', location.state.gameId);
      console.log('받은 gameName:', location.state.gameName);
    }
  }, [location.state]);

  const handleEditGame = (gameDetail) => {
    console.log('gameDetail:', gameDetail);
    navigate('/companion/games/update', { 
      state: {gameDetail: gameDetail, fileUrl: fileUrls[gameDetail.gameSeq]} 
    });
  };

  const handleGoToList = () => {
    navigate('/companion/dashboard', { 
      state: { isGame: true } 
    });
  };

  // 게임 상세 정보와 함께 이미지 URL도 조회
  const fetchGameDetail = async () => {
    if (!gameId) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${window.API_BASE_URL}/companion/games/list?gameId=${gameId}`);
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
                    <div className="game-title">{gameDetail.gameDesc}</div>
                    <div className="game-answer">정답 : {gameDetail.answerText}</div>
                  </div>
                  <button className="game-edit-btn" onClick={() => handleEditGame(gameDetail)}>수정</button>
                </div>
              </div>
            ))}
          </div>

          <button type="button" className="btn btn-login" onClick={handleGoToList}>목록으로</button>
        </div>
      </main>
      
      {/* 알람 모달 */}
      <AlarmModal />
      <FamilyFooter />
    </div>
  );
}

export default FamilyGameListPage;
