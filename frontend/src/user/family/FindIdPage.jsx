import {useEffect, useState} from 'react';
import { useNavigate } from 'react-router-dom';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import LoginHeader from '@/components/layout/header/LoginHeader';


function FindIdPage() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        email: '',
        verificationCode: ''
    });

    const [isEmailSent, setIsEmailSent] = useState(false);
    const [isEmailVerified, setIsEmailVerified] = useState(false);
    const [foundLoginId, setFoundLoginId] = useState(''); //0811수정
    const [error, setError] = useState('');
    const [timeLeft, setTimeLeft] = useState(0); // 남은 시간 (초)

    // 에러 메시지 자동 사라지게 하는 함수
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
        if (timeLeft > 0 && !isEmailVerified) {
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
    }, [timeLeft, isEmailVerified]);

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

    // 아이디 찾기용 이메일 인증번호 발송
    const handleSendEmail = async () => {
        if (!formData.email.trim()) {
            showError('이메일을 입력해주세요.');
            return;
        }

        try {
            const response = await fetch(`${window.API_BASE_URL}/api/auth/findId/email/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
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

    // 아이디 찾기 (인증번호 확인 + 아이디 조회)
    const handleFindId = async (e) => {
        e.preventDefault();

        if (!formData.email.trim()) {
            showError('이메일을 입력해주세요.');
            return;
        }

        if (!formData.verificationCode.trim()) {
            showError('인증번호를 입력해주세요.');
            return;
        }

        if (timeLeft <= 0) {
            showError('인증번호가 만료되었습니다. 다시 요청해주세요.');
            return;
        }

        try {
            const response = await fetch(`${window.API_BASE_URL}/api/auth/findId`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: formData.email,
                    code: formData.verificationCode
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                setIsEmailVerified(true);
                setFoundLoginId(data.loginId);
                setTimeLeft(0); // 타이머 정지
                setError('');
            } else {
                showError(data.message || '인증번호가 올바르지 않거나 아이디를 찾을 수 없습니다.');
            }
        } catch (error) {
            console.error('아이디 찾기 실패:', error);
            showError('서버 연결에 실패했습니다.');
        }
    };

    // 인증번호 재전송
    const handleResendEmail = () => {
        setTimeLeft(0);
        setIsEmailSent(false);
        setFormData(prev => ({ ...prev, verificationCode: '' }));
        handleSendEmail();
    };


  return (
    <div className="app-container">
      <LoginHeader title="아이디 찾기" />

      <main className="content-area signup-con">
        <form className="find-id-form" onSubmit={handleFindId}>
          <div className="form-control-con">
            <div className="input-group-custom">
              <input type="text"  name="email" className="form-control flex-grow-1" placeholder="회원가입시 입력한 이메일" value={formData.email} onChange={handleChange} disabled={isEmailVerified} />
              <button type="button" className="btn btn-custom" onClick={handleSendEmail} disabled={isEmailVerified}>인증번호 받기</button>
            </div>
          </div>

          <div className="form-control-con">
            <input type="text" name="verificationCode" className="form-control" placeholder="인증번호를 입력하세요." value={formData.verificationCode} onChange={handleChange} disabled={isEmailVerified || timeLeft <= 0}/>
          </div>




            {timeLeft > 0 && !isEmailVerified && (
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

            {timeLeft === 0 && isEmailSent && !isEmailVerified && (
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

            {foundLoginId  && (
                <div className="find-id-result-con2">가입하신 아이디는<br/><span>{foundLoginId }</span>입니다.</div>
            )}

            {error && (
                <div className="alert alert-danger mb-3" role="alert">
                    {error}
                </div>
            )}

            {!isEmailVerified ? (
                <button type="submit" className="btn btn-login" onClick={handleFindId}>
                    아이디 찾기
                </button>
            ) : (
                <div className="button-group" style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                    <button
                        type="button"
                        className="btn btn-login"
                        style={{ flex: 1 }}
                        onClick={() => {
                            navigate('/');
                        }}
                    >
                        로그인
                    </button>
                    <button
                        type="button"
                        className="btn btn-login"
                        style={{ flex: 1 }}
                        onClick={() => {
                            navigate('/findpw');
                        }}
                    >
                        비밀번호 찾기
                    </button>
                </div>
            )}

        </form>
      </main>

      <div className="spacer"></div>
    </div>
  );
}

export default FindIdPage;
