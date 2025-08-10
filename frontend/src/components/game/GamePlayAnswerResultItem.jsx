const GamePlayAnswerResultItem = ({ answerResult, gameData, handleNextQuestion }) => {
  return (
      <>
        {/* 상단 문구 */}
        <div className="greeting">
          {answerResult.isCorrect === 'Y' ? '정확합니다!' : '아쉽습니다!'}
        </div>

        {/* 아이콘 */}
        <div className="game-icon-con">
          <div className={`game-icon ${answerResult.isCorrect === 'Y' ? 'good' : 'bad'}`}></div>
        </div>

        {/* 결과 정보 */}
        <section className="content-con">
          <div className="game-phrase">
            {answerResult.isCorrect ? '잘하셨어요!' : '다음엔 맞출 거예요!'}
          </div>
          <div className="score-wrap">
            <div className={`score-con ${answerResult.isCorrect === 'Y' ? 'good' : 'bad'}`}>
              <span>{`+${answerResult.score}점`}</span>
            </div>
          </div>
        </section>

        {/* 다음 문제 버튼 */}
        <button
            className="btn btn-patient mt-3"
            onClick={handleNextQuestion}
        >
          {gameData.gameSeq >= gameData.totalQuestions ? '결과 확인' : '다음 문제'}
        </button>
      </>
  );
};

export default GamePlayAnswerResultItem;