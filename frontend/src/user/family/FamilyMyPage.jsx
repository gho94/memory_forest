import React, { useState, useEffect } from 'react';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';

import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';
import AlarmModal from '@/components/modal/AlarmModal';
import { useNavigate } from 'react-router-dom';

function FamilyMyPage() {
  const [showAlarmModal, setShowAlarmModal] = useState(false);
  const [genderCodes, setGenderCodes] = useState([]);
  const [userTypeCodes, setUserTypeCodes] = useState([]);
  const [statusCodes, setStatusCodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentUserId, setCurrentUserId] = useState('');
  const navigate = useNavigate();

  const [currentUser, setCurrentUser] = useState({
    userId: '',
    userName: '',
    loginId: '',    
    password: '',
    email: '',
    phone: '',
    birthDate: '',
    genderCode: '',
    userTypeCode: '',
    loginType: '',
    statusCode: ''
  });

    useEffect(() => {
        const getCurrentUserId = async () => {
            const userInfo = sessionStorage.getItem('user');

            if (userInfo) {
                try {
                    const user = JSON.parse(userInfo);
                    console.log('SessionStorage에서 가져온 사용자 정보:', user);
                    setCurrentUserId(user.userId);
                    return; // SessionStorage 있으면 종료
                } catch (error) {
                    console.error('SessionStorage 파싱 오류:', error);
                    sessionStorage.removeItem('user'); // 잘못된 데이터 제거
                }
            }

            // 2단계: SessionStorage에 없으면 서버 세션에서 조회
            console.log('SessionStorage에 사용자 정보가 없음. 서버 세션에서 조회 중...');

            try {
                const response = await fetch(`${window.API_BASE_URL}/api/auth/session-info`, {
                    credentials: 'include' // 쿠키 포함
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        console.log('서버 세션에서 가져온 사용자 정보:', data);

                        // SessionStorage에 저장
                        const userInfo = {
                            userId: data.userId,
                            userName: data.userName,
                            userTypeCode: data.userTypeCode,
                            email: data.email,
                            loginType: data.loginType,
                            loginId: data.loginId
                        };
                        sessionStorage.setItem('user', JSON.stringify(userInfo));
                        setCurrentUserId(data.userId);
                    } else {
                        console.error('세션 정보 조회 실패:', data.message);
                        navigate('/login');
                    }
                } else {
                    console.error('세션 정보 조회 실패:', response.status);
                    navigate('/login');
                }
            } catch (error) {
                console.error('세션 정보 조회 중 오류:', error);
                navigate('/login');
            }
        };

        getCurrentUserId();
    }, [navigate]);

  useEffect(() => {
    const getCurrentUser = async () => {
      if (!currentUserId) {
        return;
      }
      
      const response = await fetch(`${window.API_BASE_URL}/companion/user/mypage?userId=${currentUserId}`);
      console.log('사용자 정보 조회 요청:', currentUserId);
      
      if (response.ok) {
        const data = await response.json();
        console.log('사용자 정보:', data);
        
        const sanitizedData = Object.keys(data).reduce((acc, key) => {
          acc[key] = data[key] === null ? '' : data[key];
          return acc;
        }, {});
        setCurrentUser(sanitizedData);
      } else {
        console.error('사용자 정보 조회 실패:', response.status);
      }
    };
    getCurrentUser();
  }, [currentUserId]);

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

  useEffect(() => {
    const loadCommonCodes = async () => {
      const genderData = await fetchCommonCodes('A10005');
      setGenderCodes(genderData);
    };

    loadCommonCodes();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    if (name === 'birthDate' && value) {
      const selectedDate = new Date(value);
      const today = new Date();
      today.setHours(23, 59, 59, 999);
      
      if (selectedDate > today) {
        alert('미래의 날짜를 선택할 수 없습니다.');
        return;
      }
    }
    
    setCurrentUser(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {    
    e.preventDefault();

    // 현재 로그인된 사용자 ID가 없으면 처리 중단
    if (!currentUserId) {
      alert('로그인 정보를 찾을 수 없습니다. 다시 로그인해주세요.');
      return;
    }

    try {
      // 전송할 데이터 구성
      const requestData = {
        ...currentUser,
        loginId: currentUserId, // 현재 로그인된 사용자 ID
      };

      console.log('전송할 데이터:', requestData);

      const response = await fetch(`${window.API_BASE_URL}/companion/user/update`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('수정 성공:', result);
        alert('기록자가 성공적으로 수정되었습니다.');

        navigate('/companion/dashboard');
      } else {
        console.error('수정 실패:', response.status);
        alert('수정에 실패했습니다. 다시 시도해주세요.');
      }

    } catch (error) {
      console.error('수정 실패:', error);
      alert('수정 중 오류가 발생했습니다.');
    }
  };

  const handleWithdrawal = async () => {
    if (!window.confirm('정말로 회원탈퇴하시겠습니까?')) {
      return;
    }

    try {
      const requestData = {
        ...currentUser,
        statusCode: 'A20008'
      };

      console.log('회원탈퇴 요청 데이터:', requestData);

      const response = await fetch(`${window.API_BASE_URL}/companion/user/update`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('회원탈퇴 성공:', result);
        alert('회원탈퇴가 완료되었습니다.');
        
        sessionStorage.removeItem('user');
        localStorage.removeItem('user');
        
        navigate('/');
      } else {
        console.error('회원탈퇴 실패:', response.status);
        alert('회원탈퇴에 실패했습니다. 다시 시도해주세요.');
      }
    } catch (error) {
      console.error('회원탈퇴 중 오류:', error);
      alert('회원탈퇴 중 오류가 발생했습니다.');
    }
  };

  const handleLogout = () => {
    sessionStorage.removeItem('user');
    localStorage.removeItem('user');
    navigate('/');
  };

  return (
    <div className="app-container d-flex flex-column">
      <FamilyHeader />

      <main className="content-area guardian-con">
        <div className="menu-title">
          <div>나의 정보</div>
          <div></div>
        </div>

        <form className="signup-form patient-signup-form" onSubmit={handleSubmit}>

          <div className="form-control-con">
            <input 
              type="text" 
              className="form-control" 
              placeholder="이름" 
              name="userName"
              value={currentUser.userName}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-control-con">
            <input 
              type="text" 
              className="form-control" 
              placeholder="로그인 아이디" 
              name="loginId"
              value={currentUser.loginId}
              onChange={handleInputChange}
              required
              disabled
            />
          </div>

          <div className="form-control-con">
            <input 
              type="password" 
              className="form-control" 
              placeholder="비밀번호" 
              name="password"
              required
              disabled
            />
          </div>

          <div className="form-control-con">
            <input 
              type="email" 
              className="form-control" 
              placeholder="이메일" 
              name="email"
              value={currentUser.email}
              onChange={handleInputChange}
              required
              disabled
            />
          </div>

          <div className="form-control-con">
            <input 
              type="tel" 
              className="form-control" 
              placeholder="전화번호" 
              name="phone"
              value={currentUser.phone}
              onChange={handleInputChange}
            />
          </div>

          <div className="form-control-con">
            <input 
              type="date" 
              className="form-control" 
              placeholder="생년월일" 
              name="birthDate"
              value={currentUser.birthDate}
              onChange={handleInputChange}
              max={new Date().toISOString().split('T')[0]}
            />
            <i className="bi bi-calendar calendar-icon"></i>
          </div>

          <div className="form-control-con">
            <select 
              className="form-control" 
              placeholder="성별" 
              name="genderCode"
              value={currentUser.genderCode}
              onChange={handleInputChange}
            >
              <option disabled hidden value="">
                성별
              </option>
              {genderCodes.map((code) => (
                <option key={code.codeId} value={code.codeId}>
                  {code.codeName}
                </option>
              ))}
            </select>
          </div>

          <button type="submit" className="btn btn-login">
            수정하기
          </button>

          <div className="row mypage-btn-con col-12 d-flex justify-between">
            <button type="button" className="col-6 mypage-btn btn btn-login" onClick={handleLogout}>
              로그아웃
            </button>
            <button type="button" className="col-6 mypage-btn btn btn-login" onClick={handleWithdrawal}>
              회원탈퇴
            </button>
          </div>
        </form>
      </main>

      {/* 알람 모달 */}
      <AlarmModal />

      <FamilyFooter />
    </div>
  );
}

export default FamilyMyPage;
