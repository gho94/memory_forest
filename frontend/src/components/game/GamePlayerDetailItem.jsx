import { useEffect, useState } from 'react';
import useFileUrl from '@/hooks/common/useFileUrl';
const GamePlayerDetailItem = ({ game }) => {
    const { fetchFileUrl, isLoading } = useFileUrl();
    const [backgroundImage, setBackgroundImage] = useState('');
    const allOptions = [
        { text: game.answerText, name: game.isCorrect === 'Y' ? 'correct-selected' : 'correct-answer' },
        { text: game.wrongOption1, name: game.isCorrect === 'Y' || game.selectedOption !== 2 ? 'normal-option' : 'wrong-selected' },
        { text: game.wrongOption2, name: game.isCorrect === 'Y' || game.selectedOption !== 3 ? 'normal-option' : 'wrong-selected' },
        { text: game.wrongOption3, name: game.isCorrect === 'Y' || game.selectedOption !== 4 ? 'normal-option' : 'wrong-selected' }
    ].filter(option => option.text); // null/undefined 제거
    useEffect(() => {
        const loadImage = async () => {
            if (game.fileId) {
                try {
                    const fileUrl = await fetchFileUrl(game.fileId);
                    setBackgroundImage(fileUrl);
                } catch (error) {
                    console.error('이미지 로드 실패:', error);
                    setBackgroundImage('');
                }
            }
        };

        loadImage();
    }, [game.fileId, fetchFileUrl]);


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

    return (
        <div className="game-item">
            <div className="game-content">
                <div className="game-image"
                     style={{
                         backgroundImage: backgroundImage ? `url(${backgroundImage})` : 'none',
                     }}></div>
                <div className="options-container">
                    <div className="user-info">
                        <span className="score">{game.scoreEarned}점</span>
                        <span>{game.gameSeq}번 문제</span>
                    </div>
                    <div className="options-grid">
                        {shuffledOptions.map((option, index) => {
                            return (
                                <div key={index} className={'option-btn '+option.name}>
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