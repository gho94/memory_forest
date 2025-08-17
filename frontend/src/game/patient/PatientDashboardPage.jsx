import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom'; // 추가
import '@/assets/css/common.css';
import '@/assets/css/patient.css';
import PatientHeader from '@/components/layout/header/PatientHeader';
import PatientFooter from '@/components/layout/footer/PatientFooter';

// 스켈레톤 컴포넌트 분리
const SkeletonBox = ({ width, height, className = '' }) => (
    <div
        className={`skeleton ${className}`}
        style={{ width, height }}
    />
);

const SkeletonUI = () => (
    <div className="app-container d-flex flex-column">
      <PatientHeader />
      <main className="content-area patient-con">
        <div className="greeting">
          안녕하세요, <br />
          <SkeletonBox width="80px" height="24px" className="skeleton-username" />님!
        </div>

        <section className="content-con">
          <SkeletonBox width="120px" height="20px" className="mb-3" />

          <div className="progress skeleton-progress-wrapper">
            <SkeletonBox width="60%" height="100%" className="skeleton-progress-bar" />
          </div>

          <SkeletonBox width="100px" height="16px" className="mt-2" />
        </section>

        <button className="btn btn-patient skeleton-button mt-3" disabled>
          게임 시작하기
        </button>

        <SkeletonBox width="120px" height="16px" className="skeleton-score mt-3" />
      </main>
      <PatientFooter />
    </div>
);

// 게임 상태별 설정을 객체로 관리
const GAME_CONFIG = {
  IN_PROGRESS: {
    title: '진행중인 게임',
    buttonText: '게임 계속하기',
    getUrl: (gameId) => `/recorder/game?gameId=${gameId}`
  },
  NEW_GAME: {
    title: '오늘의 게임',
    buttonText: '게임 시작하기',
    getUrl: (gameId) => `/recorder/game?gameId=${gameId}`
  },
  COMPLETED: {
    title: (beforeDays) => beforeDays > 0 ? `${beforeDays}일 전 완료한 게임` : '오늘 완료한 게임',
    buttonText: '결과보기',
    getUrl: (gameId) => `/recorder/chart?gameId=${gameId}`
  }
};


const useSharedAccess = () => {
    const { accessCode } = useParams();
    const location = useLocation();
    const navigate = useNavigate();
    const [isSharedAccess, setIsSharedAccess] = useState(false);
    const [sharedLoginComplete, setSharedLoginComplete] = useState(false)

    useEffect(() => {
        if (location.pathname.startsWith('/patient-view/') && accessCode) {
            setIsSharedAccess(true);

            // 공유 링크 로그인 처리
            const loginWithAccessCode = async () => {
                try {
                    console.log('공유 링크 접근 코드:', accessCode);
                    const response = await fetch(`${window.API_BASE_URL}/api/recorder/login/${accessCode}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        credentials: 'include',
                        body: JSON.stringify({ accessCode: accessCode })
                    });

                    const data = await response.json();
                    console.log('공유 링크 로그인 응답:', data);

                    if (data.success) {
                        console.log('공유 링크 로그인 성공 - 환자ID:', data.patientId);
                        if (data.patientId && data.patientName) {
                            const userInfo = {
                                userId: data.patientId,
                                userName: data.patientName,
                                isSharedAccess: true
                            };
                            sessionStorage.setItem('user', JSON.stringify(userInfo));
                        }

                        setSharedLoginComplete(true);

                        //redirect처리 추가하기
                        navigate('/recorder/dashboard', { replace: true });

                    } else {
                        console.error('공유 링크 로그인 실패:', data.message);
                        alert(data.message || '유효하지 않은 접근 링크입니다.');
                        // 실패시 메인 페이지로 리다이렉트
                        window.location.href = '/';
                    }
                } catch (error) {
                    console.error('로그인 요청 실패:', error);
                    alert('로그인 처리 중 오류가 발생했습니다.');
                }
            };

            loginWithAccessCode();
        } else {
            setSharedLoginComplete(true);
        }
    }, [accessCode, location.pathname, navigate]);

    return { isSharedAccess, sharedLoginComplete };
};

// 커스텀 훅으로 데이터 fetching 로직 분리 수정
const useDashboardData = (sharedLoginComplete) => {
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // 공유 접근의 경우 로그인 완료를 기다림
        if (!sharedLoginComplete) {
            return;
        }

        const fetchDashboardData = async () => {
            try {
                setLoading(true);
                const response = await fetch(`${window.API_BASE_URL}/recorder/game/dashboard`, {
                    method: 'GET',
                    credentials: 'include',
                });

                // 응답이 JSON인지 먼저 확인
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error('서버에서 JSON이 아닌 응답을 받았습니다.');
                }

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: 대시보드 데이터를 불러오지 못했습니다.`);
                }

                const data = await response.json();
                setDashboardData(data);
            } catch (err) {
                console.error('API 에러:', err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, [sharedLoginComplete]);

    return { dashboardData, loading, error };
};

// 커스텀 훅으로 데이터 fetching 로직 분리
// const useDashboardData = () => {
//   const [dashboardData, setDashboardData] = useState(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);
//
//   useEffect(() => {
//     const fetchDashboardData = async () => {
//       try {
//         setLoading(true);
//         const response = await fetch(`${window.API_BASE_URL}/recorder/game/dashboard`, {
//           method: 'GET',
//           credentials: 'include',
//         });
//
//         // 응답이 JSON인지 먼저 확인
//         const contentType = response.headers.get('content-type');
//         if (!contentType || !contentType.includes('application/json')) {
//           throw new Error('서버에서 JSON이 아닌 응답을 받았습니다.');
//         }
//
//         if (!response.ok) {
//           throw new Error(`HTTP ${response.status}: 대시보드 데이터를 불러오지 못했습니다.`);
//         }
//
//         const data = await response.json();
//         setDashboardData(data);
//       } catch (err) {
//         console.error('API 에러:', err); // 디버깅용
//         setError(err.message);
//       } finally {
//         setLoading(false);
//       }
//     };
//
//     fetchDashboardData();
//   }, []);
//
//   return { dashboardData, loading, error };
// };

// 게임 정보 계산 로직을 커스텀 훅으로 분리
const useGameInfo = (dashboardData) => {
  const getProgressPercentage = () => {
    if (!dashboardData) return 0;
    return dashboardData.totalQuestions > 0
        ? (dashboardData.currentProgress / dashboardData.totalQuestions) * 100
        : 0;
  };

  const getGameConfig = () => {
    if (!dashboardData) return GAME_CONFIG.NEW_GAME;
    return GAME_CONFIG[dashboardData.status] || GAME_CONFIG.NEW_GAME;
  };

  const getTitleText = () => {
    const config = getGameConfig();
    if (typeof config.title === 'function') {
      return config.title(dashboardData?.beforeDays);
    }
    return config.title;
  };

  const handleButtonClick = () => {
    if (!dashboardData) return;
    const config = getGameConfig();
    const url = config.getUrl(dashboardData.gameId);
    window.location.href = url;
  };

  return {
    progressPercentage: getProgressPercentage(),
    titleText: getTitleText(),
    buttonText: getGameConfig().buttonText,
    handleButtonClick,
  };
};

// 에러 컴포넌트 분리
const ErrorMessage = ({ error }) => (
    <div className="app-container d-flex flex-column">
      <PatientHeader />
      <main className="content-area patient-con">
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      </main>
      <PatientFooter />
    </div>
);

// 메인 컴포넌트
function PatientDashboardPage() {
  const { isSharedAccess, sharedLoginComplete } = useSharedAccess(); // 추가
  const { dashboardData, loading, error } = useDashboardData(sharedLoginComplete);
  const {
    progressPercentage,
    titleText,
    buttonText,
    handleButtonClick,
  } = useGameInfo(dashboardData);

  //로딩 표시 넣기
    if (isSharedAccess && !sharedLoginComplete) {
        return <SkeletonUI />;
    }


  if (loading) return <SkeletonUI />;
  if (error) return <ErrorMessage error={error} />;
  if (!dashboardData) return <ErrorMessage error="대시보드 데이터를 불러올 수 없습니다." />;
  return (
      <div className="app-container d-flex flex-column">
        <PatientHeader />

        <main className="content-area patient-con">
          <div className="greeting">
            안녕하세요, <br />
            <span className="user-name">{dashboardData.userName}님!</span>
          </div>

          <section className="content-con">
            <div className="title">{titleText}</div>

            <div className="progress">
              <div
                  className="progress-bar"
                  role="progressbar"
                  style={{ width: `${progressPercentage}%` }}
                  aria-valuenow={dashboardData.currentProgress}
                  aria-valuemin={0}
                  aria-valuemax={dashboardData.totalQuestions}
              />
            </div>

            <div className="progress-text">
              {dashboardData.currentProgress} / {dashboardData.totalQuestions} 문제 완료
            </div>
          </section>

          <button
              className="btn btn-patient mt-3"
              onClick={handleButtonClick}
          >
            {buttonText}
          </button>

          {dashboardData.recentAccuracyRate!==0 && dashboardData.recentAccuracyRate!==null && (
              <div className="recent-score">최근 정확도 : {dashboardData.recentAccuracyRate}%</div>
          )}
        </main>
        <PatientFooter />
      </div>
  );
}

export default PatientDashboardPage;