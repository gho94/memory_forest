const GamePlayResultItem = ({ totalScore, correctCount, accuracyRate, gameId }) => {

  return (
      <>
        <div className="greeting">게임 완료!</div>

        <div className="game-sum-score-con">
          총 점수 : <span>{totalScore}</span>점
        </div>

        <div className="row">
          <div className="col-6">
            <section className="content-con">
              <div className="result-number">{correctCount}</div>
              <div className="result-text">정답 수</div>
            </section>
          </div>
          <div className="col-6">
            <section className="content-con">
              <div className="result-number">{accuracyRate}%</div>
              <div className="result-text">정답률</div>
            </section>
          </div>
        </div>

          <button
              onClick={() => window.location.href = `/recorder/chart?gameId=${gameId}`}
              className="btn btn-patient"
          >진행도 확인</button>
      </>
  );
};
export default GamePlayResultItem;