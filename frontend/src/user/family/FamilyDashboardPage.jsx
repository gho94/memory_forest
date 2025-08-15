import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';
import AlarmModal from '@/components/modal/AlarmModal';
// import AccountShareModal from '@/components/modal/AccountShareModal';

import '@/assets/css/common.css';
import '@/assets/css/family.css';
import QRCode from 'qrcode';
import useFileUrl from '@/hooks/common/useFileUrl';

function FamilyDashboardPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isGame, setIsGame] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [gameList, setGameList] = useState([]);
  const [fileUrls, setFileUrls] = useState({});
  const [recorderList, setRecorderList] = useState([]);
  const [userId, setUserId] = useState('');
  const [relationshipCodes, setRelationshipCodes] = useState({});
  
  const [selectedPatients, setSelectedPatients] = useState([]);
  const [gameName, setGameName] = useState('');

  const [shareUrl, setShareUrl] = useState('');
  const [currentPatientName, setCurrentPatientName] = useState('');
  const [isSharing, setIsSharing] = useState(false);
  const [qrCodeDataUrl, setQrCodeDataUrl] = useState('');
  const { fetchFileUrl, isLoading } = useFileUrl();


  const fetchCommonCodes = async (parentCodeId) => {
    try {
      setLoading(true);
      const response = await fetch(`${window.API_BASE_URL}/api/common-codes?parentCodeID=${parentCodeId || ''}`);
      if (response.ok) {
        const data = await response.json();
        return data;
      } else {
        console.error('공통코드 조회 실패:', response.status);
        return [];
      }
    } catch (error) {
      console.error('공통코드 조회 중 오류:', error);
      return [];
    } finally {
      setLoading(false);
    }
  };

  const getRelationshipName = (code) => {
    return relationshipCodes.find(item => item.codeId === code)?.codeName || code;
  };

  useEffect(() => {
    const loadCommonCodes = async () => {
      const relationshipData = await fetchCommonCodes('A10003');
      console.log('관계 코드 매핑:', relationshipData);
      setRelationshipCodes(relationshipData);
    };
    loadCommonCodes();
  }, []);


  // useEffect(() => {
  //   const getUserInfo = () => {
  //     const userInfo = localStorage.getItem('user');
  //     if (userInfo) {
  //       try {
  //         const user = JSON.parse(userInfo);
  //         console.log('사용자 정보:', user);
  //         setUserId(user.userId);
  //       } catch (error) {
  //         console.error('사용자 정보 파싱 오류:', error);
  //       }
  //     } else {
  //       console.log('localStorage에 사용자 정보가 없습니다.');
  //     }
  //   };
  //
  //   getUserInfo();
  // }, []);



    useEffect(() => {
        const getUserInfo = async () => {
            const userInfo = sessionStorage.getItem('user');
            if (userInfo) {
                try {
                    const user = JSON.parse(userInfo);
                    console.log('SessionStorage에서 가져온 사용자 정보:', user);
                    setUserId(user.userId);
                    return; // sessionStorage에 있으면 여기서 끝
                } catch (error) {
                    console.error('사용자 정보 파싱 오류:', error);
                    sessionStorage.removeItem('user'); // 잘못된 데이터 제거
                }
            }

            console.log('SessionStorage에 사용자 정보가 없음. 서버 세션에서 조회 중...');

            try {
                const response = await fetch(`${window.API_BASE_URL}/api/auth/session-info`, {
                    credentials: 'include' // 쿠키 포함
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        console.log('서버 세션에서 가져온 사용자 정보:', data);

                        // sessionStorage 저장
                        const userInfo = {
                            userId: data.userId,
                            userName: data.userName,
                            userTypeCode: data.userTypeCode,
                            email: data.email,
                            loginType: data.loginType,
                            loginId: data.loginId
                        };
                        sessionStorage.setItem('user', JSON.stringify(userInfo));
                        setUserId(data.userId);
                    } else {
                        console.error('세션 정보 조회 실패:', data.message);
                    }
                } else {
                    console.error('세션 정보 조회 실패:', response.status);
                }
            } catch (error) {
                console.error('세션 정보 조회 중 오류:', error);
            }
        };

        getUserInfo();
    }, []);


  useEffect(() => {
    if (location.state) {
      if (location.state.isGame !== undefined) {
        setIsGame(location.state.isGame);
      }
      if (location.state.gameName) {
        setGameName(location.state.gameName);
      }
    }
  }, [location.state]);



    // 공유 버튼 클릭 처리
    const handleShareClick = async (patientId, patientName) => {
        if (isSharing) return; // 중복 클릭 방지

        setIsSharing(true);

        try {
            console.log('공유 링크 생성 시작 - 환자ID:', patientId, '이름:', patientName);

            const response = await fetch(`${window.API_BASE_URL}/api/recorder/${patientId}/share`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include' // 세션 쿠키 포함
            });

            const data = await response.json();
            console.log('서버 응답:', data);

            if (data.success) {
                setShareUrl(data.shareUrl);
                setCurrentPatientName(patientName);

                // 모달 열기
                document.getElementById('toggle-account-modal').checked = true;

                console.log('공유 링크 생성 성공:', data.shareUrl);
                generateQRCode(data.shareUrl);
            } else {
                alert(data.message || '공유 링크 생성에 실패했습니다.');
            }
        } catch (error) {
            console.error('공유 링크 생성 실패:', error);
            alert('공유 링크 생성에 실패했습니다. 네트워크를 확인해주세요.');
        } finally {
            setIsSharing(false);
        }
    };

    // 카카오톡 공유 함수
    const shareKakao = () => {
        if (!window.Kakao) {
            alert('카카오 SDK가 로드되지 않았습니다.');
            return;
        }

        if (!shareUrl) {
            alert('공유할 링크가 없습니다.');
            return;
        }

        try {
            window.Kakao.Share.sendDefault({
                objectType: 'feed',
                content: {
                    title: '환자 프로필 공유',
                    description: `${currentPatientName}님의 의료 정보를 확인해보세요`,
                    link: {
                        mobileWebUrl: shareUrl,
                        webUrl: shareUrl
                    }
                }
            });
        } catch (error) {
            console.error('카카오톡 공유 실패:', error);
            alert('카카오톡 공유에 실패했습니다.');
        }
    };
    
    const generateQRCode = async (shareUrl) => {
      try {
        const currentUrl = shareUrl;
        console.log('currentUrl', currentUrl);
        const qrCodeDataUrl = await QRCode.toDataURL(currentUrl);
        console.log('QR코드 생성 완료');
        console.log('qrCodeDataUrl', qrCodeDataUrl);
        setQrCodeDataUrl(qrCodeDataUrl);
      } catch (err) {
        console.error('QR코드 생성 오류:', err);
      }
    };
  
    // 링크 복사 함수
    const copyLink = () => {
        if (!shareUrl) {
            alert('공유할 링크가 없습니다.');
            return;
        }

        navigator.clipboard.writeText(shareUrl)
            .then(() => {
                alert('링크가 복사되었습니다!');
            })
            .catch(() => {
                // 복사 실패 시 대체 방법
                const textArea = document.createElement('textarea');
                textArea.value = shareUrl;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('링크가 복사되었습니다!');
            });
    };

  const handleNextStep = () => {
    if (selectedPatients.length === 0) {
      alert('환자를 선택해주세요.');
      return;
    }
    
    navigate('/companion/games/create', { 
      state: { 
        gameName: gameName, 
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

      const urlPromises = data.map(async (game) => {
        if (game.fileId) {
          const fileUrl = await fetchFileUrl(game.fileId);
          return { gameId: game.gameId, fileUrl };
        }
        return { gameId: game.gameId, fileUrl: null };
      });
      
      const urlResults = await Promise.all(urlPromises);
      const urlMap = {};
      urlResults.forEach(result => {
        if (result.fileUrl) {
          urlMap[result.gameId] = result.fileUrl;
        }
      });
      
      setFileUrls(urlMap);

      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };  

  const fetchRecorderList = async (userId) => {
    try {
      setLoading(true);
      const response = await fetch(`${window.API_BASE_URL}/api/recorder/list?userId=${userId}`);
      if (!response.ok) {
        throw new Error('데이터를 가져오는데 실패했습니다.');
      }
      const data = await response.json();
      console.log('받아온 기록자 데이터:', data);
      setRecorderList(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    console.log('userId 변경됨:', userId);
    if (userId) {
      fetchRecorderList(userId);
    }
  }, [userId]);

  useEffect(() => {
    fetchGameList();
  }, []);

  const handlePatientSelection = (patientId) => {
    setSelectedPatients(prev => {
      if (prev.includes(patientId)) {
        return prev.filter(id => id !== patientId);
      } else {
        return [...prev, patientId];
      }
    });
  };

  // 체크박스가 선택되었는지 확인하는 함수
  const isPatientSelected = (patientId) => {
    return selectedPatients.includes(patientId);
  };

  const calculateAge = (birthDate) => {
    const today = new Date();
    const birthDateObj = new Date(birthDate);
    return today.getFullYear() - birthDateObj.getFullYear();
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
            <div className="fw-bold fs-5">총 기록자 : <span>{recorderList.length}</span>명</div>
            <button className="btn btn-add" onClick={() => navigate('/companion/profileadd')}>기록자 추가</button>
          </div>

          <div className="d-flex flex-column gap-3 card-box-con">
            {recorderList.map((recorder) => ( 
            <div className="card-box" key={recorder.userId}>
              <div className="d-flex align-items-center">
                <div className="profile-img"></div>
                <div className="flex-grow-1 text-start">
                  <div className="main-desc">
                    <span className="patient-name">{recorder.userName}</span>
                    <span className="patient-age">({recorder.birthDate ? calculateAge(recorder.birthDate) : ''}세)</span>
                  </div>
                  <div className="extra-desc">최근 활동 : 2025-06-20</div>
                </div>
                <button className="btn-detail me-1">
                  <div className="btn more-btn"></div>
                </button>
                <button className="btn-detail" onClick={() => handleShareClick(recorder.userId, recorder.userName)}>
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
            ))}
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

          <div className="d-flex flex-column gap-3 card-box2-con">
            {gameList.map((game) => (              
            <div className="card-box" key={game.gameId}>
              <div className="d-flex align-items-center">
                <div className="game-img">
                  <img src={fileUrls[game.gameId]} alt="문제 이미지" height="100%" width="100%" />
                </div>
                <div className="flex-grow-1 text-start">
                  <div className="main-desc">
                    <span className="patient-name">{game.gameName}</span>
                  </div>
                  <div className="target-desc">
                    대상자 : {game.players.map(player => player.userName).join(', ')}
                  </div>
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
              <div className="qr-code" style={{ backgroundImage: `url(${qrCodeDataUrl})` }}></div>
            </div>
            <div className="row gx-0 share-icon-con">
              <div className="col-6 me-4 kakaotalk-icon" onClick={shareKakao}></div>
              <div className="col-6 link-icon" onClick={copyLink}></div>
            </div>
              {shareUrl && (
                  <div className="share-url-display mt-2">
                      <input
                          type="text"
                          value={shareUrl}
                          readOnly
                          className="form-control"
                          style={{ fontSize: '12px' }}
                      />
                  </div>
              )}
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
                value={gameName}
                onChange={(e) => setGameName(e.target.value)}
              />
            </div>
          </div>
          <div className="game-modal-title mb-1">게임 대상</div>
          <div className="modal-body-scroll d-flex flex-column gap-3">
            {recorderList.map((recorder) => (
              <div key={recorder.userId} className="account-info align-items-start d-flex gap-2">
                <div>
                  <input 
                    type="checkbox" 
                    className="modal-checkbox"
                    checked={isPatientSelected(recorder.userId)}
                    onChange={() => handlePatientSelection(recorder.userId)}
                  />
                </div>
                <div>
                  <div className="patient-con">
                    <span className="patient-name">{recorder.userName}</span>
                    <span className="patient-reg-date">({recorder.birthDate ? calculateAge(recorder.birthDate) : ''}세, {getRelationshipName(recorder.relationshipCode)})</span>
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