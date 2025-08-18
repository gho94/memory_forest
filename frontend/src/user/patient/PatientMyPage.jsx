import { useState, useEffect } from 'react';
import '@/assets/css/common.css';
import '@/assets/css/patient.css';
import PatientHeader from '@/components/layout/header/PatientHeader';
import PatientFooter from '@/components/layout/footer/PatientFooter';

function PatientMyPage() {
  const [userInfo, setUserInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 생년월일 포맷팅 함수 (YYYY-MM-DD -> YYYY년 MM월 DD일)
  const formatBirthDate = (birthDate) => {
    if (!birthDate) return '';
    const date = new Date(birthDate);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}년 ${month}월 ${day}일`;
  };

  // API 호출 함수
  const fetchUserInfo = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${window.API_BASE_URL}/recorder/user/mypage`, {
        credentials: 'include'
      });
      if (!response.ok) {
        throw new Error('사용자 정보를 가져오는데 실패했습니다.');
      }
      const data = await response.json();
      setUserInfo(data);
    } catch (err) {
      setError(err.message);
      console.error('API 호출 오류:', err);
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 시 데이터 로드
  useEffect(() => {
    fetchUserInfo();
  }, []);

  // 에러가 발생했을 때
  if (error) {
    return (
        <div className="app-container d-flex flex-column">
          <PatientHeader />
          <main className="content-area patient-con">
            <div className="greeting">오류가 발생했습니다</div>
            <section className="content-con">
              <div className="information-con">
                <div style={{color: 'red'}}>{error}</div>
              </div>
            </section>
          </main>
          <PatientFooter/>
        </div>
    );
  }

  // 정상적으로 데이터를 가져왔을 때
  return (
      <div className="app-container d-flex flex-column">
        <PatientHeader />
        <main className="content-area patient-con">
          <div className="greeting">나의 정보</div>
          <section className="content-con">
            <div className="information-con">
              <div>이름 : <span>{userInfo?.userName}</span></div>
              <div>성별 : <span>{userInfo?.genderCode}</span></div>
              <div>생년월일 : <br/><span>{formatBirthDate(userInfo?.birthDate)}</span></div>
            </div>
          </section>
          <div className="greeting">동행자 정보</div>
          <section className="content-con">
            <div className="information-con">
              <div>이름 : <span>{userInfo?.companionName}</span></div>
              <div>관계 : <span>{userInfo?.relationshipCode}</span></div>
              <div>연락처 : <br/><span>{userInfo?.companionPhone}</span></div>
            </div>
          </section>
        </main>
        <PatientFooter/>
      </div>
  );
}

export default PatientMyPage;