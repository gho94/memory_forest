import '@/assets/css/common.css';
import '@/assets/css/patient.css';
import PatientHeader from '@/components/layout/header/PatientHeader';
import PatientFooter from '@/components/layout/footer/PatientFooter';

function PatientGameAnswerResultPage({ isCorrect, score }) {
  return (
    <div className="app-container d-flex flex-column">
      <PatientHeader />

      <main className="content-area patient-con">
        {/* 상단 문구 */}
        <div className="greeting">
          {isCorrect ? '정확합니다!' : '아쉽습니다!'}
        </div>

        {/* 아이콘 */}
        <div className="game-icon-con">
          <div className={`game-icon ${isCorrect ? 'good' : 'bad'}`}></div>
        </div>

        {/* 결과 정보 */}
        <section className="content-con">
          <div className="game-phrase">
            {isCorrect ? '잘하셨어요!' : '다음엔 맞출 거예요!'}
          </div>
          <div className="score-wrap">
            <div className={`score-con ${isCorrect ? 'good' : 'bad'}`}>
              <span>{`+${score}점`}</span>
            </div>
          </div>
        </section>

        {/* 다음 문제 버튼 */}
        <button className="btn btn-patient mt-3">다음 문제</button>
      </main>

      <PatientFooter />
    </div>
  );
}

export default PatientGameAnswerResultPage;
