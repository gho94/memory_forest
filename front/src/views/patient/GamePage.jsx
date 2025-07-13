import '../../assets/css/patient/GamePage.css';
import '../../assets/css/common/common.css';
import PatientHeader from '../../components/layout/header/PatientHeader';
import PatientFooter from '../../components/layout/footer/PatientFooter';
import gameExampleImg from '../../assets/images/game_example.jpg';

function GamePage() {
  return (
    <div className="app-container d-flex flex-column">
      <PatientHeader />

      <main className="content-area patient-con">
        <section className="content-con mb-16">
          <div className="progress">
            <div
              className="progress-bar"
              role="progressbar"
              style={{ width: "60%" }}
              aria-valuenow={6}
              aria-valuemin={0}
              aria-valuemax={10}
            ></div>
            <div className="progress-label">6 / 10</div>
          </div>
        </section>

        <section className="content-con game-img-con">
          <img className="game-img" src={gameExampleImg} alt="게임 예시" />
        </section>

        <div className="row">
          <div className="col-6">
            <button className="btn btn-game w-100">달</button>
          </div>
          <div className="col-6">
            <button className="btn btn-game w-100">해수욕장</button>
          </div>
        </div>
        <div className="row">
          <div className="col-6">
            <button className="btn btn-game w-100">달</button>
          </div>
          <div className="col-6">
            <button className="btn btn-game w-100">을왕리해수욕장!!!!</button>
          </div>
        </div>
      </main>

      <PatientFooter />
    </div>
  );
}

export default GamePage;
