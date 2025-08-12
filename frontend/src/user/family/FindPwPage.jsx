import { useState , useEffect} from 'react';
import { useNavigate } from 'react-router-dom';
import LoginHeader from '@/components/layout/header/LoginHeader';
import '@/assets/css/common.css';
import '@/assets/css/login.css';

function FindPwPage() {

    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        loginId: '',
        email: '',
        verificationCode: ''
    });

    const [isEmailSent, setIsEmailSent] = useState(false);
    const [error, setError] = useState('');
    const [timeLeft, setTimeLeft] = useState(0); // 남은 시간 (초)

    // 에러 메시지 자동 사라지게 하는 함수 => 근데 왜 안없어지니~~?
    const showError = (message) => {
        setError(message);
        if (message) {
            setTimeout(() => {
                setError('');
            }, 5000);
        }
    };

    // 타이머 관리
    useEffect(() => {
        let timer;
        if (timeLeft > 0) {
            timer = setInterval(() => {
                setTimeLeft(prev => {
                    if (prev <= 1) {
                        return 0; // 시간 종료
                    }
                    return prev - 1;
                });
            }, 1000);
        }
        return () => clearInterval(timer);
    }, [timeLeft]);

    // 남은 시간을 mm:ss 형식으로 변환
    const formatTime = (seconds) => {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    };

    // 입력값 변경 핸들러
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));

        if (error) setError('');
    };

    // 비밀번호 재설정용 인증번호 발송
    const handleSendEmail = async () => {
        if (!formData.loginId.trim()) {
            showError('아이디를 입력해주세요.');
            return;
        }

        if (!formData.email.trim()) {
            showError('이메일을 입력해주세요.');
            return;
        }

        try {
            const response = await fetch(`http://localhost:8080/api/auth/password/reset/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    loginId: formData.loginId,
                    email: formData.email
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                setIsEmailSent(true);
                setTimeLeft(300); // 5분 = 300초
                // alert('인증번호가 이메일로 전송되었습니다.');
                //로직 추가
            } else {
                // 남은 시간이 있는 경우 특별 처리
                if (data.remainingSeconds) {
                    const minutes = Math.floor(data.remainingSeconds / 60);
                    const seconds = data.remainingSeconds % 60;
                    const timeMessage = minutes > 0 ?
                        `${minutes}분 ${seconds}초` :
                        `${seconds}초`;
                    showError(`이미 유효한 인증번호가 있습니다. ${timeMessage} 후 다시 시도해주세요.`);

                    // 기존에 발송된 상태로 설정하고 남은 시간 표시
                    setIsEmailSent(true);
                    setTimeLeft(data.remainingSeconds);
                } else {
                    showError(data.message || '인증번호 전송에 실패했습니다.');
                }
            }
        } catch (error) {
            console.error('인증번호 전송 실패:', error);
            showError('서버 연결에 실패했습니다.');
        }
    };

    // 인증번호 재전송
    const handleResendEmail = () => {
        setTimeLeft(0);
        setFormData(prev => ({ ...prev, verificationCode: '' }));
        handleSendEmail();
    };

    // 인증번호 확인 및 다음 단계로 이동
    const handleVerifyAndNext = async (e) => {
        e.preventDefault();
        if (!formData.loginId.trim() || !formData.email.trim()) {
            showError('아이디와 이메일을 입력해주세요.');
            return;
        }

        if (!formData.verificationCode.trim()) {
            showError('인증번호를 입력해주세요.');
            return;
        }

        if (timeLeft <= 0 && isEmailSent) {
            showError('인증번호가 만료되었습니다. 다시 요청해주세요.');
            return;
        }

        // alert('인증이 완료되었습니다! 비밀번호 재설정 페이지로 이동합니다.');
        navigate('/resetPw', { state: { loginId: formData.loginId, email: formData.email, verificationCode: formData.verificationCode, verified: true } });
    };

    return (
        <div className="app-container">
            <LoginHeader title="비밀번호 찾기" />

            <main className="content-area signup-con">
                <div className="find-id-form">


                    {/* 아이디 입력 */}
                    <div className="form-control-con">
                        <input type="text" name="loginId" className="form-control" placeholder="아이디" value={formData.loginId} onChange={handleChange}/>
                    </div>

                    {/* 이메일 입력 + 인증번호 받기 */}
                    <div className="form-control-con">
                        <div className="input-group-custom">
                            <input type="email" name="email" className="form-control flex-grow-1" placeholder="이메일" value={formData.email} onChange={handleChange}/>
                            <button type="button" className="btn btn-custom" onClick={handleSendEmail} disabled={timeLeft > 0}>인증번호 받기</button>
                        </div>
                    </div>

                    {/* 인증번호 입력 */}
                        <div className="form-control-con">
                            <input type="text" name="verificationCode" className="form-control" placeholder="인증번호를 입력하세요." value={formData.verificationCode} onChange={handleChange} disabled={timeLeft <= 0 && isEmailSent}/>
                        </div>

                    {/* 타이머 표시 (이메일 전송 후에만) */}
                    {timeLeft > 0 && (
                        <div className="form-text-info fw-semibold" style={{
                            color: timeLeft <= 60 ? '#dc3545' : '#6c757d',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center'
                        }}>
                            <span>* 남은 시간: {formatTime(timeLeft)}</span>
                            {timeLeft <= 60 && (
                                <button
                                    type="button"
                                    onClick={handleResendEmail}
                                    style={{
                                        background: 'none',
                                        border: 'none',
                                        color: '#007bff',
                                        textDecoration: 'underline',
                                        cursor: 'pointer',
                                        fontSize: '12px'
                                    }}
                                >
                                    재전송
                                </button>
                            )}
                        </div>
                    )}

                    {/* 시간 만료 메시지 */}
                    {timeLeft === 0 && isEmailSent && (
                        <div className="form-text-invalid fw-semibold">
                            * 인증번호가 만료되었습니다.
                            <button
                                type="button"
                                onClick={handleResendEmail}
                                style={{
                                    background: 'none',
                                    border: 'none',
                                    color: '#007bff',
                                    textDecoration: 'underline',
                                    cursor: 'pointer',
                                    marginLeft: '5px'
                                }}
                            >
                                다시 받기
                            </button>
                        </div>
                    )}

                {/* 에러 메시지 */}
                    {error && (
                        <div className="alert alert-danger mb-3" role="alert">
                            {error}
                        </div>
                    )}

                    <button type="submit" className="btn btn-login" onClick={handleVerifyAndNext} disabled={timeLeft <= 0 && isEmailSent}>비밀번호 재설정</button>
                </div>
            </main>
            <div className="spacer"></div>
        </div>
    );
}

export default FindPwPage;