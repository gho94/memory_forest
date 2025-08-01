import '@/assets/css/common.css';
import '@/assets/css/patient.css';
import PatientHeader from '@/components/layout/header/PatientHeader';
import PatientFooter from '@/components/layout/footer/PatientFooter';

function PatientChartPage() {
  return (
    <div className="app-container d-flex flex-column">
      <PatientHeader />

      <main className="content-area patient-con game-result-area">
        <div className="greeting">나의 진행도</div>

        <section className="content-con">
          <div className="chart-con">
            {/* 진행도 차트 들어갈 자리 */}
          </div>
        </section>

        <div className="row">
          <div className="col-6">
            <section className="content-con">
              <div className="result-number">234</div>
              <div className="result-text">총 게임 횟수</div>
            </section>
          </div>
          <div className="col-6">
            <section className="content-con">
              <div className="result-number">82</div>
              <div className="result-text">평균<br />점수</div>
            </section>
          </div>
        </div>
      </main>

      <PatientFooter />
    </div>
  );
}

export default PatientChartPage;
