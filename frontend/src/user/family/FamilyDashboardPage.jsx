import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';
import AlarmModal from '@/components/modal/AlarmModal';
// import AccountShareModal from '@/components/modal/AccountShareModal';

import '@/assets/css/common.css';
import '@/assets/css/family.css';

function FamilyDashboardPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isGame, setIsGame] = useState(false);
  const [gameTitle, setGameTitle] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [gameList, setGameList] = useState([]);
  
  // 샘플 환자 데이터
  const [samplePatients, setSamplePatients] = useState([
    { userId: 'U0001', userName: '김철수', age: 78, relation: '부', selected: false },
    { userId: 'U0002', userName: '이영희', age: 75, relation: '모', selected: false },
    { userId: 'U0003', userName: '박민수', age: 82, relation: '할아버지', selected: false }
  ]);
  
  const [selectedPatients, setSelectedPatients] = useState([]);

  useEffect(() => {
    if (location.state) {
      if (location.state.isGame !== undefined) {
        setIsGame(location.state.isGame);
      }
      if (location.state.gameTitle) {
        setGameTitle(location.state.gameTitle);
      }
    }
  }, [location.state]);

  const handleNextStep = () => {
    if (selectedPatients.length === 0) {
      alert('환자를 선택해주세요.');
      return;
    }
    
    navigate('/companion/games/create', { 
      state: { 
        gameTitle: gameTitle, 
        selectedPatients: selectedPatients 
      } 
    });
  };

  const handleGameList = (gameId, gameName) => {
    navigate('/companion/games/list', { 
      state: { gameId: gameId, gameName: gameName } 
    });
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return '';
      
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      
      return `${year}-${month}-${day}`;
    } catch (error) {
      console.error('날짜 포맷팅 오류:', error);
      return '';
    }
  };

  const fetchGameList = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${window.API_BASE_URL}/companion/dashboard`);
      if (!response.ok) {
        throw new Error('데이터를 가져오는데 실패했습니다.');
      }
      const data = await response.json();
      console.log('받아온 게임 데이터:', data);
      setGameList(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };  

  useEffect(() => {
    fetchGameList();
  }, []);

  const handlePatientSelection = (patientId) => {
    setSamplePatients(prev => 
      prev.map(patient => 
        patient.userId === patientId 
          ? { ...patient, selected: !patient.selected }
          : patient
      )
    );
    
    setSelectedPatients(prev => {
      if (prev.includes(patientId)) {
        return prev.filter(id => id !== patientId);
      } else {
        return [...prev, patientId];
      }
    });
  };

  return (
    <div className="app-container d-flex flex-column">
      <FamilyHeader />

      <main className="content-area guardian-con">
        <div className="greeting-con">
          <div className="greeting">
            <div className="fw-bold mb-2 fs-5">
              <span>아이디</span> 님, 안녕하세요!
            </div>
            <div>
              <span className="sub-text">모두 함께 하는</span> <br />
              <span className="fw-bold fs-6">기억 숲</span>
              <span className="sub-text">시간을 만들어보세요.</span>
            </div>
          </div>
        </div>

        <ul className="menu-tab-con nav nav-tabs mb-2">
          <li className="nav-item">            
            <a className={`nav-link ${isGame ? '' : 'active'}`} href="#" onClick={() => setIsGame(false)}>계정</a>
          </li>
          <li className="nav-item">
            <a className={`nav-link ${isGame ? 'active' : ''}`} href="#" onClick={() => setIsGame(true)}>게임목록</a>
          </li>
        </ul>

        <div style={{ display: isGame ? 'none' : 'block' }} className="account-con mx-3">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <div className="fw-bold fs-5">총 기록자 : <span>8</span>명</div>
            <button className="btn btn-add">기록자 추가</button>
          </div>

          <div className="d-flex flex-column gap-3 card-box-con">
            <div className="card-box">
              <div className="d-flex align-items-center">
                <div className="profile-img"></div>
                <div className="flex-grow-1 text-start">
                  <div className="main-desc">
                    <span className="patient-name">환자01</span>
                    <span className="patient-age">(78세)</span>
                  </div>
                  <div className="extra-desc">최근 활동 : 2025-06-20</div>
                </div>
                <button className="btn-detail me-1">
                  <div className="btn more-btn"></div>
                </button>
                <button className="btn-detail">
                  <label htmlFor="toggle-account-modal" className="btn share-btn"></label>
                </button>
              </div>
              <div className="row risk-con mt-2">
                <div className="risk-title col-3">평균 위험도</div>
                <div className="col-9 risk-bar-con d-flex align-items-center">
                  <div className="risk-bar-bg">
                    <div className="risk-bar-fill"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div style={{ display: isGame ? 'block' : 'none' }} className="game-con mx-3">
          <div className="search-filter-box d-flex align-items-center gap-2 mb-3">
            <input type="checkbox" id="search-dropdown-toggle" />
            <div className="search-dropdown-wrapper">
              <label htmlFor="search-dropdown-toggle" className="search-dropdown-display">전체</label>
              <ul className="search-dropdown-options">
                <li>전체</li>
                <li>제목</li>
                <li>설명</li>
                <li>정답</li>
              </ul>
            </div>
            <div className="search-input-box position-relative flex-grow-1">
              <input type="text" className="search-input" placeholder="검색할 내용을 입력하세요." />
              <div className="search-icon"></div>
            </div>
          </div>

          <div className="d-flex justify-content-between align-items-center mb-3">
            <div className="fw-bold fs-5">총 게임 : <span>{gameList.length}</span>개</div>
            <label htmlFor="toggle-game-modal" className="btn btn-add">게임 추가</label>
          </div>

          <div className="d-flex flex-column gap-3 card-box-con">
            {gameList.map((game) => (              
            <div className="card-box" key={game.gameId}>
              <div className="d-flex align-items-center">
                <div className="game-img"></div>
                <div className="flex-grow-1 text-start">
                  <div className="main-desc">
                    <span className="patient-name">{game.gameName}</span>
                  </div>
                  <div className="target-desc">대상자 : 환자01, 환자02</div>
                  <div className="extra-desc">생성일 : {formatDate(game.createdAt)}</div>
                </div>
                <button className="btn-detail me-1" onClick={() => handleGameList(game.gameId, game.gameName)}>
                  <div className="btn more-btn"></div>
                </button>
              </div>
            </div>              
            ))}
          </div>
        </div>
      </main>

      <AlarmModal />
      {/* 계정 공유 모달 */}
      {/* <AccountShareModal /> */}
      <input type="checkbox" id="toggle-account-modal" />
      <div className="modal-overlay account-modal-overlay">
        <div className="position-relative custom-modal">
          <label htmlFor="toggle-account-modal" className="custom-close">&times;</label>
          <div className="text-center mb-3">
            <div className="center-group">
              <div className="logo" aria-label="기억 숲 로고"></div>
              <div className="title">계정 공유</div>
            </div>
          </div>
          <div className="modal-body-scroll d-flex flex-column gap-3">
            <div className="qr-code-con">
              <div className="qr-code">qr</div>
            </div>
            <div className="row gx-0 share-icon-con">
              <div className="col-6 me-4 kakaotalk-icon"></div>
              <div className="col-6 link-icon"></div>
            </div>
          </div>
        </div>
      </div>

      {/* 게임 추가 모달 */}
      <input type="checkbox" id="toggle-game-modal" />
      <div className="modal-overlay game-modal-overlay">
        <div className="position-relative custom-modal">
          <label htmlFor="toggle-game-modal" className="custom-close">&times;</label>
          <div className="text-center mb-3">
            <div className="center-group">
              <div className="logo" aria-label="기억 숲 로고"></div>
              <div className="title">게임 추가</div>
            </div>
          </div>
          <div className="row gx-0 game-name-con">
            <div className="game-modal-title col-3">게임 제목</div>
            <div className="col-1">:</div>
            <div className="col-8">
              <input 
                type="text" 
                className="game-name" 
                placeholder="게임 제목을 입력하세요" 
                value={gameTitle}
                onChange={(e) => setGameTitle(e.target.value)}
              />
            </div>
          </div>
          <div className="game-modal-title mb-1">게임 대상</div>
          <div className="modal-body-scroll d-flex flex-column gap-3">
            {samplePatients.map((patient) => (
              <div key={patient.userId} className="account-info align-items-start d-flex gap-2">
                <div>
                  <input 
                    type="checkbox" 
                    className="modal-checkbox"
                    checked={patient.selected}
                    onChange={() => handlePatientSelection(patient.userId)}
                  />
                </div>
                <div>
                  <div className="patient-con">
                    <span className="patient-name">{patient.userName}</span>
                    <span className="patient-reg-date">({patient.age}세, {patient.relation})</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <button type="button" className="btn btn-modal" onClick={handleNextStep}>다음 단계</button>
        </div>
      </div>

      <FamilyFooter />
    </div>
  );
}

export default FamilyDashboardPage;