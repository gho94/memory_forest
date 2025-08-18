import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function AlarmModal() {
    const navigate = useNavigate();

    // 알림 데이터를 저장할 상태
    const [alarms, setAlarms] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // 컴포넌트가 마운트될 때 API 호출
    useEffect(() => {
        const fetchAlarms = async () => {
            try {
                setLoading(true);
                const response = await fetch(`${window.API_BASE_URL}/api/alarms`, {credentials: 'include'});

                if (!response.ok) {
                    throw new Error('알림 데이터를 가져오는데 실패했습니다.');
                }

                const data = await response.json();
                setAlarms(data);
            } catch (err) {
                setError(err.message);
                console.error('알림 데이터 가져오기 오류:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchAlarms();
    }, []);

    const handleAlarmClick = async (alarm) => {
        // 읽지 않은 알림인 경우에만 읽음 처리
        if (alarm.isRead === 'N') {
            await markAlarmAsRead(alarm.alarmId);
        }

        // 페이지 이동
        navigate(`/companion/detail?userId=${alarm.userId}&gameId=${alarm.gameId}`);
    };

    // 알림 읽음 처리 API 호출
    const markAlarmAsRead = async (alarmId) => {
        try {
            const response = await fetch(`${window.API_BASE_URL}/api/alarms/${alarmId}/read`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error('알림 읽음 처리에 실패했습니다.');
            }

            // 성공적으로 읽음 처리되면 로컬 상태도 업데이트
            setAlarms(prevAlarms =>
                prevAlarms.map(alarm =>
                    alarm.alarmId === alarmId
                        ? { ...alarm, isRead: 'Y' }
                        : alarm
                )
            );
        } catch (err) {
            console.error('알림 읽음 처리 오류:', err);
            // 에러가 발생해도 페이지 이동은 계속 진행
        }
    };

    // 날짜 포맷팅 함수
    const formatDate = (dateString) => {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');

        return `${year}.${month}.${day} ${hours}:${minutes}`;
    };

    return (
        <>
            {/* 모달을 열기 위한 체크박스 */}
            <input type="checkbox" id="toggle-alarm-modal" className="toggle-checkbox"/>
            {/* 모달 오버레이 */}
            <div className="modal-overlay alarm-modal-overlay">
                <div className="position-relative custom-modal">
                    <label htmlFor="toggle-alarm-modal" className="custom-close">&times;</label>
                    <div className="text-center mb-3">
                        <div className="center-group">
                            <div className="logo" aria-label="기억 숲 로고"></div>
                            <div className="title">알림</div>
                        </div>
                    </div>
                    <div className="modal-body-scroll d-flex flex-column gap-3">
                        {loading && (
                            <div className="text-center p-5">
                                <p>알림을 불러오는 중...</p>
                            </div>
                        )}

                        {error && (
                            <div className="text-center p-5">
                                <p style={{color: 'red'}}>오류: {error}</p>
                            </div>
                        )}

                        {!loading && !error && alarms.length === 0 && (
                            <div className="text-center p-5">
                                <p>알림이 없습니다.</p>
                            </div>
                        )}

                        {!loading && !error && alarms.map((alarm) => (
                            <div key={alarm.alarmId}
                                 className={`alert-card ${alarm.isRead === 'N' ? 'active' : 'inactive'} d-flex align-items-start gap-2`}
                                 onClick={() => handleAlarmClick(alarm)}
                                 style={{ cursor: 'pointer' }}>
                                <div className="profile-img" alt="avatar"/>
                                <div>
                                    <div className="patient-con">
                                        <span className="patient-name">{alarm.userName}</span>
                                        <span className="patient-reg-date">{formatDate(alarm.createdAt)}</span>
                                    </div>
                                    <div className="alarm-content">
                                        {alarm.message.split('\n').map((line, index) => (
                                            <span key={index}>
                                                {line}
                                                {index < alarm.message.split('\n').length - 1 && <br/>}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </>
    );
}

export default AlarmModal;