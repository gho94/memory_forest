import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';

import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';
import useFileUpload from '@/hooks/common/useFileUpload';

function FamilyGameCreatePage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [problems, setProblems] = useState([]);
  const [gameTitle, setGameTitle] = useState('');
  const [selectedPatients, setSelectedPatients] = useState([]);
  const totalProblems = problems.length;
  const progressPercentage = Math.min((totalProblems / 10) * 100, 100);

  const gameData = {
    gameName: gameTitle,
    gameDesc: '',
    gameDetails: problems,
    totalProblems: totalProblems,
    selectedPatients: selectedPatients
  }  
  const [currentProblem, setCurrentProblem] = useState({
    fileId: null,
    answerText: '',
    description: ''
  });

  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);
  const [fileImage, setFileImage] = useState(null);
  const { uploadFile } = useFileUpload();

  useEffect(() => {
    if (location.state && location.state.gameTitle) {
      setGameTitle(location.state.gameTitle);
      setSelectedPatients(location.state.selectedPatients);
    }
  }, [location.state]);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setFile(file);

    const reader = new FileReader();
    reader.onload = (e) => {
      setFileImage(e.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleAddProblem = async () => {
    if (!file || !currentProblem.answerText.trim()) {
      alert('파일과 정답 단어를 모두 입력해주세요.');
      return;
    }

    const uploadedFileId = await uploadFile(file);
    
    if (uploadedFileId) {
      const newProblem = {
        ...currentProblem,
        fileId: uploadedFileId
      };

      setProblems(prev => [...prev, newProblem]);
      setCurrentProblem({
        fileId: null,
        answerText: '',
        description: ''
      });

      if (fileInputRef.current) {
        fileInputRef.current.value = '';
        setFile(null);
        setFileImage(null);
      }
    }
  };

  const handleCreateGame = async () => {
    if (!gameTitle.trim()) {
      alert('게임 제목을 입력해주세요.');
      return;
    }

    if (problems.length === 0) {
      alert('최소 하나의 문제를 추가해주세요.');
      return;
    }

    console.log('gameData:', gameData);

    try {
      const response = await fetch(`${window.API_BASE_URL}/api/game`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(gameData),
      });

      if (response.ok) {
        const result = await response.json();
        alert('게임이 성공적으로 생성되었습니다!');
        console.log('게임 생성 성공:', result);
        navigate('/companion/games/complete', {
          state: {
            gameData: gameData
          }
        });
      } else {
        console.error('게임 생성 실패');
        alert('게임 생성에 실패했습니다.');
      }
    } catch (error) {
      console.error('게임 생성 중 오류 발생:', error);
      alert('게임 생성 중 오류가 발생했습니다.');
    }
  }

  return (
    <div className="app-container d-flex flex-column">
      <FamilyHeader />

      <main className="content-area guardian-con">
        <div className="menu-title">
          <div>게임 만들기</div>
          <div className="progress">
            <div
              className="progress-bar"
              role="progressbar"
              style={{ width: `${progressPercentage}%` }}
              aria-valuenow={totalProblems}
              aria-valuemin="0"
              aria-valuemax="10"
            ></div>
            <div className="progress-label">{totalProblems} / 10</div>
          </div>
        </div>

        <form className="signup-form game-signup-form">
          <div className="form-control-con">
            <input
              type="text"
              className="form-control"
              placeholder="게임 제목을 입력하세요."
              value={gameTitle}
              onChange={(e) => setGameTitle(e.target.value)}
            />
          </div>

          <div className="form-control-con">
            <div className="form-control game-file-desc-con">
              {file && <img src={fileImage} style={{ width: 'auto', height: '100%' }} />}              
              <div className={`game-file-desc mb-3 mt-2 ${file ? 'd-none' : ''}`}>
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
                className={`btn btn-add ${file ? 'd-none' : ''}`}
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
              value={currentProblem.answerText}
              onChange={(e) => setCurrentProblem(prev => ({
                ...prev,
                answerText: e.target.value
              }))}
            />
          </div>

          <div className="form-control-con">
            <textarea
              className="form-control"
              placeholder="설명을 입력하세요."
              value={currentProblem.description}
              onChange={(e) => setCurrentProblem(prev => ({
                ...prev,
                description: e.target.value
              }))}
            ></textarea>
          </div>

          <button 
            type="button" 
            className="btn btn-login"
            onClick={handleAddProblem}
            disabled={!file || !currentProblem.answerText.trim()}
          >
            다음 문제 추가하기
          </button>
          <button 
            type="button" 
            className="btn btn-login" 
            onClick={handleCreateGame}
          >
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
