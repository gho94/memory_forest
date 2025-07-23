import '../../assets/css/common.css';
import '../../assets/css/Patient.css'; 
import PatientHeader from '../../components/layout/header/PatientHeader';
import PatientFooter from '../../components/layout/footer/PatientFooter';

function PatientDashboardPage() {
  return (
    <div className="app-container d-flex flex-column">
      <PatientHeader />

      <main className="content-area patient-con">
        <div className="greeting">
          안녕하세요, <br />
          <span className="user-name">홍길동</span>님!
        </div>

        <section className="content-con">
          <div className="title">오늘의 게임</div>
          <div className="progress">
            <div
              className="progress-bar"
              role="progressbar"
              style={{ width: '60%' }}
              aria-valuenow={6}
              aria-valuemin={0}
              aria-valuemax={10}
            ></div>
          </div>
          <div className="progress-text">6 / 10 문제 완료</div>
        </section>

        <button className="btn btn-patient mt-3">게임 시작하기</button>

        <div className="recent-score">최근 점수 : 85점</div>
      </main>

      <PatientFooter />
    </div>
  );
}

export default PatientDashboardPage;
