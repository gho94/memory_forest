import { useState, useEffect, useRef } from 'react';

export const GAME_STATE = {
    PLAYING: 'playing',
    ANSWER_RESULT: 'answer_result',
    GAME_COMPLETE: 'game_complete'
};

export const useGamePlayLogic = () => {
    const [gameData, setGameData] = useState(null);
    const [gameState, setGameState] = useState(GAME_STATE.PLAYING);
    const [answerResult, setAnswerResult] = useState({isCorrect: false, score: 0});
    const [totalScore, setTotalScore] = useState(0);
    const [correctCount, setCorrectCount] = useState(0);
    const [buttonOptions, setButtonOptions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [accuracyRate, setAccuracyRate] = useState(0);
    const apiFetchTimeRef = useRef(null);
    const queryParams = new URLSearchParams(location.search);

    // 게임 ID 검증
    const gameId = queryParams.get('gameId');
    if (!gameId) {
        console.error('게임 ID가 없습니다.');
    }

    // Fisher-Yates 셔플 알고리즘
    const shuffleArray = (array) => {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    };

    // 버튼 옵션 생성
    const createButtonOptions = (data) => {
        if (!data) return [];
        const options = [
            {text: data.answerText, value: 1},
            {text: data.wrongOption1, value: 2},
            {text: data.wrongOption2, value: 3},
            {text: data.wrongOption3, value: 4}
        ];
        return shuffleArray(options);
    };

    // 초기 게임 데이터 로드
    useEffect(() => {
        let isMounted = true; // cleanup flag 추가v

        const loadGameData = async () => {
            if (!isMounted) return; // 이미 cleanup됐으면 실행 안함

            try {
                setLoading(true);
                const apiUrl = `${window.API_BASE_URL}/recorder/game/play/${queryParams.get('gameId')}`;

                const response = await fetch(apiUrl, {
                    method: 'GET',
                    credentials: 'include',
                });

                if (!isMounted) return; // fetch 완료 후에도 확인

                if (!response.ok) {
                    try {
                        await fetchGameResult();
                    } catch (resultErr) {
                        console.error('게임 결과 조회도 실패:', resultErr);
                        if (isMounted) {
                            setError('게임 데이터를 불러올 수 없습니다.');
                        }
                    }
                    return; // 여기서 함수 종료
                }

                const data = await response.json();
                setGameData(data);
                setButtonOptions(createButtonOptions(data));
                apiFetchTimeRef.current = Date.now();

            } catch (err) {
                if (!isMounted) return;
                setError(err.message);
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        };

        loadGameData();

        return () => {
            isMounted = false; // cleanup
        };
    }, []);

    // 답안 선택 처리
    const handleAnswerSelect = async (selectedOption) => {
        const isCorrect = selectedOption === 1 ? 'Y' : 'N';
        const answerTimeMs = Date.now()-apiFetchTimeRef.current;

        const response = await fetch(`${window.API_BASE_URL}/recorder/game/play`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                isCorrect: isCorrect,
                selectedOption: selectedOption,
                answerTimeMs: answerTimeMs,
                gameId : queryParams.get('gameId'),
                gameSeq : gameData.gameSeq
            })
        });
        if (!response.ok) {
            throw new Error('코드 추가 실패');
        }

        const score = await response.json();

        setAnswerResult({isCorrect, score});
        setGameState(GAME_STATE.ANSWER_RESULT);
    };

    // 다음 문제로 이동
    const handleNextQuestion = async () => {
        if (gameData.gameSeq >= gameData.totalQuestions) {
            await fetchGameResult();
        } else {
            try {
                const apiUrl = `${window.API_BASE_URL}/recorder/game/play/${queryParams.get('gameId')}`;
                const response = await fetch(apiUrl, {
                    method: 'GET',
                    credentials: 'include',
                });

                if (!response.ok) {
                    throw new Error('게임 조회 처리에 실패했습니다.');
                }

                const nextGameData = await response.json();
                setGameData(nextGameData);
                setButtonOptions(createButtonOptions(nextGameData));
                setGameState(GAME_STATE.PLAYING);
                apiFetchTimeRef.current = Date.now();
            } catch (err) {
                console.error('다음 문제 로드 오류:', err);
                setError(err.message);
            }
        }
    };

    const fetchGameResult = async () => {
        try {
            setLoading(true); // 명시적으로 로딩 시작
            const apiUrl = `${window.API_BASE_URL}/recorder/game/result/${queryParams.get('gameId')}`;
            const response = await fetch(apiUrl, {
                method: 'GET',
                credentials: 'include',
            });

            if (!response.ok) {
                throw new Error('게임 결과 조회 처리에 실패했습니다.');
            }

            const resultGameData = await response.json();
            setGameData(resultGameData);
            setCorrectCount(resultGameData.correctCount);
            setTotalScore(resultGameData.totalScore);
            setAccuracyRate(resultGameData.accuracyRate);
            setGameState(GAME_STATE.GAME_COMPLETE);

            return resultGameData;
        } catch (err) {
            console.error('게임 결과 조회 오류:', err);
            setError(err.message);
            throw err; // 에러 다시 던지기
        } finally {
            setLoading(false);
        }
    };


    return {
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
    };
};