import '@/assets/css/common.css';
import '@/assets/css/patient.css';
import PatientHeader from '@/components/layout/header/PatientHeader';
import PatientFooter from '@/components/layout/footer/PatientFooter';

function PatientMyPage() {
  return (
    <div className="app-container d-flex flex-column">
      <PatientHeader />

      <main className="content-area patient-con">
        <div className="mypage-greeting">나의 정보</div>

        <section className="mypage-info-con">
          <div>이름 : <span>홍길동</span></div>
          <div>성별 : <span>남성</span></div>
          <div>
            생년월일 : <br />
            <span>1900년 01월 01일</span>
          </div>
        </section>

        <div className="mypage-greeting">동행자 정보</div>

        <section className="mypage-info-con">
          <div>이름 : <span>김철수</span></div>
          <div>관계 : <span>자녀</span></div>
          <div>
            연락처 : <br />
            <span>010-0000-0000</span>
          </div>
        </section>
      </main>

      <PatientFooter />
    </div>
  );
}

export default PatientMyPage;
