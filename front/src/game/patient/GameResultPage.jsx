import '../../assets/css/common.css';
import '../../assets/css/Patient.css'; 
import PatientHeader from '../../components/layout/header/PatientHeader';
import PatientFooter from '../../components/layout/footer/PatientFooter';


function GameResultPage() {
  return (
    <div className="app-container d-flex flex-column">
      <PatientHeader />

      <main className="content-area patient-con game-result-area">
        <div className="greeting">게임 완료!</div>
        <div className="game-sum-score-con">총 점수 : <span>843</span>점</div>

        <div className="row">
          <div className="col-6">
            <section className="content-con">
              <div className="result-number">8</div>
              <div className="result-text">정답 수</div>
            </section>
          </div>
          <div className="col-6">
            <section className="content-con">
              <div className="result-number">80%</div>
              <div className="result-text">정답률</div>
            </section>
          </div>
        </div>

        <button className="btn btn-patient">진행도 확인</button>
      </main>

      <PatientFooter />
    </div>
  );
}

export default GameResultPage;
