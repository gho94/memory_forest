const GamePlayerDetailItem = ({ game }) => {
    const allOptions = [
        { text: game.answerText, isCorrect: true },
        { text: game.wrongOption1, isCorrect: false },
        { text: game.wrongOption2, isCorrect: false },
        { text: game.wrongOption3, isCorrect: false }
    ].filter(option => option.text); // null/undefined 제거

    // Fisher-Yates 셔플 알고리즘
    const shuffleArray = (array) => {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    };

    const shuffledOptions = shuffleArray(allOptions);

    // 셔플된 배열에서 정답의 인덱스 찾기
    const correctAnswerIndex = shuffledOptions.findIndex(option => option.isCorrect);

    // 사용자가 선택한 인덱스 (API에서 selectedOption 받아와야 함)
    const userSelectedIndex = (game.selectedOption || 1) - 1;

    return (
        <div className="game-item">
            <div className="game-content">
                <div className="game-image"></div>
                <div className="options-container">
                    <div className="user-info">
                        <span className="score">{game.scoreEarned}점</span>
                        <span>{game.gameSeq}번 문제</span>
                    </div>
                    <div className="options-grid">
                        {shuffledOptions.map((option, index) => {
                            let className = "option-btn normal-option";

                            if (game.isCorrect === 'Y') {
                                // 정답인 경우: 사용자가 선택한 옵션이 정답
                                if (index === userSelectedIndex) {
                                    className = "option-btn correct-selected";
                                }
                            } else {
                                // 오답인 경우
                                if (index === correctAnswerIndex) {
                                    // 정답 옵션
                                    className = "option-btn correct-answer";
                                } else if (index === userSelectedIndex) {
                                    // 사용자가 잘못 선택한 옵션
                                    className = "option-btn wrong-selected";
                                }
                            }

                            return (
                                <div key={index} className={className}>
                                    {option.text}
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default GamePlayerDetailItem;