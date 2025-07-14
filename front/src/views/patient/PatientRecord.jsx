import '../../assets/css/common/common.css';
import '../../assets/css/patient/Patient.css';
import PatientHeader from "../../components/layout/header/PatientHeader";
import PatientFooter from "../../components/layout/footer/PatientFooter";
import recordIcon from "../../assets/images/record_icon.svg";

function PatientRecord() {
  return (
    <div className="app-container d-flex flex-column">
      <PatientHeader />

      <main className="content-area patient-con">
        <div className="greeting">
          오늘 하루는
          <br />
          어땠나요?
        </div>

        <section className="content-con">
          <div className="game-icon-con">
            <div
              className="game-icon record"
              style={{
                backgroundImage: `url(${recordIcon})`,
              }}
            ></div>
          </div>
        </section>

        <div className="record_desc_con">
          <span className="dark-green-color">위 녹음 버튼 클릭 후</span>
          <span className="light-green-color">
            <br />
            기분, 날씨, 음식, 장소
            <br />
            등등<br />
            오늘 하루를 편하게
            <br />
            말씀해주세요!
          </span>
        </div>

        <button className="btn btn-patient">완료</button>
      </main>

      <PatientFooter />
    </div>
  );
}

export default PatientRecord;
