import React, { useState, useEffect } from 'react';
import useFileUrl from '@/hooks/common/useFileUrl';

const GamePlayProcessItem = ({ gameData, buttonOptions, handleAnswerSelect }) => {
    const progressPercentage = (gameData.currentProgress / gameData.totalQuestions) * 100;
    const { fetchFileUrl, isLoading } = useFileUrl();
    const [gameImagePath, setGameImagePath] = useState('');

    useEffect(() => {
        const getFileUrl = async () => {
            if (gameData?.fileId) {
                const path = await fetchFileUrl(gameData.fileId);
                setGameImagePath(path);
            }
        };
        
        getFileUrl();
    }, [gameData?.fileId, fetchFileUrl]);

    return (
        <>
            <section className="content-con mb-16">
                <div className="progress">
                    <div
                        className="progress-bar"
                        role="progressbar"
                        style={{ width: `${progressPercentage}%` }}
                        aria-valuenow={gameData.currentProgress}
                        aria-valuemin={0}
                        aria-valuemax={gameData.totalQuestions}
                    ></div>
                    <div className="progress-label">{gameData.currentProgress} / {gameData.totalQuestions}</div>
                </div>
            </section>

            <section className="content-con game-img-con">
                <img className="game-img" src={gameImagePath} alt="게임 예시" />
            </section>

            <div className="row">
                <div className="col-6">
                    <button
                        className="btn btn-game w-100"
                        data-value={buttonOptions[0].value}
                        onClick={() => handleAnswerSelect(buttonOptions[0].value)}
                    >
                        {buttonOptions[0].text}
                    </button>
                </div>
                <div className="col-6">
                    <button
                        className="btn btn-game w-100"
                        data-value={buttonOptions[1].value}
                        onClick={() => handleAnswerSelect(buttonOptions[1].value)}
                    >
                        {buttonOptions[1].text}
                    </button>
                </div>
            </div>

            <div className="row">
                <div className="col-6">
                    <button
                        className="btn btn-game w-100"
                        data-value={buttonOptions[2].value}
                        onClick={() => handleAnswerSelect(buttonOptions[2].value)}
                    >
                        {buttonOptions[2].text}
                    </button>
                </div>
                <div className="col-6">
                    <button
                        className="btn btn-game w-100"
                        data-value={buttonOptions[3].value}
                        onClick={() => handleAnswerSelect(buttonOptions[3].value)}
                    >
                        {buttonOptions[3].text}
                    </button>
                </div>
            </div>
        </>
    );
};

export default GamePlayProcessItem;