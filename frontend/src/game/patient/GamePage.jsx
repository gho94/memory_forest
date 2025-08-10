import '@/assets/css/common.css';
import '@/assets/css/patient.css';
import PatientHeader from '@/components/layout/header/PatientHeader';
import PatientFooter from '@/components/layout/footer/PatientFooter';
import {useGamePlayLogic} from '@/hooks/game/useGamePlayLogic';
import GamePlayAnswerResultItem from '@/components/game/GamePlayAnswerResultItem';
import GamePlayResultItem from '@/components/game/GamePlayResultItem';
import GamePlayProcessItem from '@/components/game/GamePlayProcessItem';

const GamePage = () => {
    const {
        gameData,
        gameState,
        answerResult,
        totalScore,
        correctCount,
        accuracyRate,
        buttonOptions,
        handleAnswerSelect,
        handleNextQuestion,
        loading,
        error,
        GAME_STATE
    } = useGamePlayLogic();
    if (loading || !gameData) {
        return (
            <div className="app-container d-flex flex-column">
                <PatientHeader />
                <main className="content-area patient-con">
                    <div className="spin-con">
                        <div className="spin"></div>
                        <div className="spin-desc">
                            게임 준비 중...
                        </div>
                    </div>
                </main>
                <PatientFooter />
            </div>
        );
    }

    // 현재 게임 상태에 따른 화면 렌더링
    const renderCurrentScreen = () => {
        switch (gameState) {
            case GAME_STATE.PLAYING:
                return (
                    <GamePlayProcessItem
                        gameData={gameData}
                        buttonOptions={buttonOptions}
                        handleAnswerSelect={handleAnswerSelect}
                    />
                );
            case GAME_STATE.ANSWER_RESULT:
                return (
                    <GamePlayAnswerResultItem
                        answerResult={answerResult}
                        gameData={gameData}
                        handleNextQuestion={handleNextQuestion}
                    />
                );
            case GAME_STATE.GAME_COMPLETE:
                return (
                    <GamePlayResultItem
                        totalScore={totalScore}
                        correctCount={correctCount}
                        accuracyRate={accuracyRate}
                        gameId={gameData.gameId}
                    />
                );
            default:
                return (
                    <GamePlayProcessItem
                        gameData={gameData}
                        buttonOptions={buttonOptions}
                        handleAnswerSelect={handleAnswerSelect}
                    />
                );
        }
    };

    return (
        <div className="app-container d-flex flex-column">
            <PatientHeader/>
            <main
                className={`content-area patient-con ${gameState === GAME_STATE.GAME_COMPLETE ? 'game-result-area' : ''}`}>
                {renderCurrentScreen()}
            </main>
            <PatientFooter/>
        </div>
    );
};

export default GamePage;