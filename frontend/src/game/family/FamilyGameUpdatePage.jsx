import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';

import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';
import useFileUpload from '@/hooks/common/useFileUpload';

function FamilyGameUpdatePage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [userId, setUserId] = useState('');
  const [gameDetail, setGameDetail] = useState({    
    gameTitle: '',
    gameDesc: '',
    fileId: null,
    answerText: ''
  });

  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);
  const [fileImage, setFileImage] = useState(null);
  const { uploadFile } = useFileUpload();

  console.log('gameDetail:', gameDetail);
  useEffect(() => {
    if (location.state && location.state.gameDetail) {
      setGameDetail(location.state.gameDetail);
      setFileImage(location.state.fileUrl);
    }
  }, [location.state]);

  useEffect(() => {
    const getUserInfo = () => {      
      const userInfo = localStorage.getItem('user');
      if (userInfo) {
        try {
          const user = JSON.parse(userInfo);
          console.log('사용자 정보:', user);
          setUserId(user.userId);
        } catch (error) {
          console.error('사용자 정보 파싱 오류:', error);
        }
      } else {
        console.log('localStorage에 사용자 정보가 없습니다.');
      }
    };

    getUserInfo();
  }, []);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setFile(file);

    const reader = new FileReader();
    reader.onload = (e) => {
      console.log('e.target.result:', e.target.result);
      setFileImage(e.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleUpdateGame = async () => {
    if (!fileImage || !gameDetail.answerText.trim() || !gameDetail.gameTitle.trim()) {
      alert('파일 또는 게임 제목과 정답 단어를 모두 입력해주세요.');
      return;
    }

    try {
      if (file) {
        const uploadFileId = await uploadFile(file);
        if (uploadFileId) {
          gameDetail.fileId = uploadFileId;
        } else {
          alert('이미지 업로드에 실패했습니다.');
          return;
        }
      }
      
      const response = await fetch(`${window.API_BASE_URL}/api/game/update`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(gameDetail),
      });

      if (response.ok) {
        const result = await response.json();
        alert('게임이 성공적으로 수정되었습니다!');
        console.log('게임 수정 성공:', result);
        navigate('/companion/games/list', {
          state: {
            gameId: result.gameId,
            gameName: result.gameName
          }
        });
      } else {
        console.error('게임 수정 실패');
        alert('게임 수정에 실패했습니다.');
      }
    } catch (error) {
      console.error('게임 수정 중 오류 발생:', error);
      alert('게임 수정 중 오류가 발생했습니다.');
    }
  }

  return (
    <div className="app-container d-flex flex-column">
      <FamilyHeader />

      <main className="content-area guardian-con">
        <div className="menu-title">
          <div>게임 수정하기</div>          
        </div>

        <form className="signup-form game-signup-form">
          <div className="form-control-con">
            <input
              type="text"
              className="form-control"
              placeholder="게임 제목을 입력하세요."
              value={gameDetail.gameTitle}
              onChange={(e) => setGameDetail(prev => ({
                ...prev,
                gameTitle: e.target.value
              }))}
            />
          </div>

          <div className="form-control-con">
            <div className="form-control game-file-desc-con">
              {file && <img src={fileImage} style={{ width: 'auto', height: '100%' }} />}   
              {file && <button className={`trash-btn icon-btn`} onClick={() => {
                setFile(null);
                setFileImage(null);
                if (fileInputRef.current) {
                  fileInputRef.current.value = '';
                }
              }}></button>}
              {!file && fileImage && <img src={fileImage} style={{ width: 'auto', height: '100%' }} />}
              {!file && fileImage && <button onClick={() => {
                setFileImage(null);
              }}>×</button>}
              <div className={`game-file-desc mb-3 mt-5 ${file || fileImage ? 'd-none' : ''}`}>
                게임에 사용할 사진을 업로드하세요.
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
              />
              <button 
                className={`btn btn-add ${file || fileImage ? 'd-none' : ''}`}
                type="button" 
                onClick={() => fileInputRef.current?.click()}
              >파일 선택</button>
            </div>
          </div>

          <div className="form-control-con">
            <input
              type="text"
              className="form-control"
              placeholder="정답 단어를 입력하세요."
              value={gameDetail.answerText}
              onChange={(e) => setGameDetail(prev => ({
                ...prev,
                answerText: e.target.value
              }))}
            />
          </div>

          <div className="form-control-con">
            <textarea
              className="form-control"
              placeholder="설명을 입력하세요."
              value={gameDetail.gameDesc}
              onChange={(e) => setGameDetail(prev => ({
                ...prev,
                gameDesc: e.target.value
              }))}
            ></textarea>
          </div>

          <button 
            type="button" 
            className="btn btn-login"
            onClick={handleUpdateGame}
            disabled={!fileImage || !gameDetail.answerText.trim() || !gameDetail.gameTitle.trim()}
          >
            게임 수정하기
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

export default FamilyGameUpdatePage;
