import React, { useState, useEffect } from 'react';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';

import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';
import AlarmModal from '@/components/modal/AlarmModal';
import { useNavigate } from 'react-router-dom';
import useFileUpload from '@/hooks/common/useFileUpload';

function PatientProfilePage() {
  const [showAlarmModal, setShowAlarmModal] = useState(false);
  const [relationshipCodes, setRelationshipCodes] = useState([]);
  const [genderCodes, setGenderCodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentUserId, setCurrentUserId] = useState('');
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [fileImage, setFileImage] = useState(null);
  const { uploadFile } = useFileUpload();
  // 드롭다운 관련 상태 추가
  const [isGenderDropdownOpen, setIsGenderDropdownOpen] = useState(false);
  const [isRelationshipDropdownOpen, setIsRelationshipDropdownOpen] = useState(false);
  const [selectedGender, setSelectedGender] = useState('성별');
  const [selectedRelationship, setSelectedRelationship] = useState('관계');
  
  const [formData, setFormData] = useState({
    userName: '',
    birthDate: '',
    genderCode: '',
    relationshipCode: '',
    userTypeCode: 'A20001', // 기록자 타입 코드 (고정값)
    fileId: null,
  });

  // 드롭다운 토글 함수들
  const toggleGenderDropdown = () => {
    setIsGenderDropdownOpen(!isGenderDropdownOpen);
    setIsRelationshipDropdownOpen(false); // 다른 드롭다운 닫기
  };

  const toggleRelationshipDropdown = () => {
    setIsRelationshipDropdownOpen(!isRelationshipDropdownOpen);
    setIsGenderDropdownOpen(false); // 다른 드롭다운 닫기
  };

  // 드롭다운 옵션 선택 함수들
  const selectGender = (genderCode, genderName) => {
    setSelectedGender(genderName);
    setFormData(prev => ({ ...prev, genderCode }));
    setIsGenderDropdownOpen(false);
  };

  const selectRelationship = (relationshipCode, relationshipName) => {
    setSelectedRelationship(relationshipName);
    setFormData(prev => ({ ...prev, relationshipCode }));
    setIsRelationshipDropdownOpen(false);
  };

  // 현재 로그인된 사용자 ID 가져오기
  // useEffect(() => {
  //   const getCurrentUserId = () => {
  //     // localStorage에서 사용자 정보 가져오기
  //     const userInfo = localStorage.getItem('user');
  //     if (userInfo) {
  //       try {
  //         const user = JSON.parse(userInfo);
  //         console.log('현재 로그인된 사용자 정보:', user);
  //         setCurrentUserId(user.userId);
  //       } catch (error) {
  //         console.error('사용자 정보 파싱 오류:', error);
  //       }
  //     } else {
  //       console.log('localStorage에 사용자 정보가 없습니다.');
  //     }
  //   };
  //
  //   getCurrentUserId();
  // }, []);


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
      const relationshipData = await fetchCommonCodes('A10003');
      setRelationshipCodes(relationshipData);

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
    
    setFormData(prev => ({
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
      let updatedFormData = { ...formData };
      
      if (file) {
        const uploadedFileId = await uploadFile(file);
        // 파일 업로드 성공 시 폼 데이터에 파일 ID 저장
        updatedFormData = { ...updatedFormData, fileId: uploadedFileId };
        console.log('uploadedFileId:', uploadedFileId);
        console.log('업데이트된 formData:', updatedFormData);
        setFormData(updatedFormData);
      }

      // 전송할 데이터 구성
      const requestData = {
        ...updatedFormData,
        loginId: currentUserId, // 현재 로그인된 사용자 ID
      };

      console.log('전송할 데이터:', requestData);

      const response = await fetch(`${window.API_BASE_URL}/api/recorder/create`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('등록 성공:', result);
        alert('기록자가 성공적으로 등록되었습니다.');

        navigate('/companion/dashboard');
      } else {
        console.error('등록 실패:', response.status);
        alert('등록에 실패했습니다. 다시 시도해주세요.');
      }

    } catch (error) {
      console.error('등록 실패:', error);
      alert('등록 중 오류가 발생했습니다.');
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setFile(file);

    const reader = new FileReader();
    reader.onload = (e) => {
      setFileImage(e.target.result);
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="app-container d-flex flex-column">
      <FamilyHeader />

      <main className="content-area guardian-con">
        <div className="menu-title">
          <div>기록자 추가</div>
          <div></div>
        </div>

        <form className="signup-form patient-signup-form" onSubmit={handleSubmit}>
          <div className="profile-upload-con">
            <div className="profile-upload">
              <input type="file" id="fileInput" accept="image/*" onChange={handleFileSelect} />
              <label htmlFor="fileInput" className="upload-label" id="previewBox">
                {file && <img src={fileImage} style={{ width: '100%', height: '100%' }} />}
                {!file && <i className="bi bi-person"></i>}
              </label>
            </div>
          </div>

          <div className="form-control-con">
            <input 
              type="text" 
              className="form-control" 
              placeholder="이름" 
              name="userName"
              value={formData.userName}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-control-con">
            <input 
              type="date" 
              className="form-control" 
              placeholder="생년월일" 
              name="birthDate"
              value={formData.birthDate}
              onChange={handleInputChange}
              max={new Date().toISOString().split('T')[0]}
              required
            />
            <i className="bi bi-calendar calendar-icon"></i>
          </div>

          <div className="form-control-con">
            <input 
              type="checkbox" 
              id="gender-dropdown-toggle" 
              checked={isGenderDropdownOpen}
              onChange={toggleGenderDropdown}
            />
            <div className="search-dropdown-wrapper">
              <label htmlFor="gender-dropdown-toggle" className="search-dropdown-display">
                {selectedGender}
              </label>
              <ul className="search-dropdown-options">
                {genderCodes.map((code) => (
                  <li key={code.codeId} onClick={() => selectGender(code.codeId, code.codeName)}>
                    {code.codeName}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="form-control-con">
            <input 
              type="checkbox" 
              id="relationship-dropdown-toggle" 
              checked={isRelationshipDropdownOpen}
              onChange={toggleRelationshipDropdown}
            />
            <div className="search-dropdown-wrapper">
              <label htmlFor="relationship-dropdown-toggle" className="search-dropdown-display">
                {selectedRelationship}
              </label>
              <ul className="search-dropdown-options">
                {relationshipCodes.map((code) => (
                  <li key={code.codeId} onClick={() => selectRelationship(code.codeId, code.codeName)}>
                    {code.codeName}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <button type="submit" className="btn btn-login">
            등록하기
          </button>
        </form>
      </main>
        <AlarmModal />
      <FamilyFooter />
    </div>
  );
}

export default PatientProfilePage;
