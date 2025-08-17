import { useState,useEffect} from 'react';
import { useNavigate } from 'react-router-dom';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import SignupHeader from '@/components/layout/header/SignupHeader';

function SignupPage() {

    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        loginId: '',
        password: '',
        confirmPassword: '',
        userName: '',
        email: '',
        verificationCode: ''
    });

    const [validation, setValidation] = useState({
        loginId: { isValid: false, message: '' },
        password: { isValid: false, message: '' },
        confirmPassword: { isValid: false, message: '' },
        email: { isValid: false, message: '' }
    });

    const [isEmailSent, setIsEmailSent] = useState(false);
    const [isEmailVerified, setIsEmailVerified] = useState(false);
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
                        return 0;
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

        // 실시간 유효성 검사
        if (name === 'password') {
            const message = validatePassword(value);
            setValidation(prev => ({
                ...prev,
                password: {
                    isValid: value.length >= 8 && value.length <= 16,
                    message
                }
            }));
        } else if (name === 'confirmPassword') {
            validateConfirmPassword(value);
        }

        if (error) setError('');
    };

    // 비밀번호 간단 유효성 검사
    const validatePassword = (password) => {
        if (password.length === 0) return '';
        if (password.length < 8 || password.length > 16) {
            return '8~16자의 영문/대소문자, 숫자, 특수문자를 사용해 주세요.';
        }
        return '';
    };

    // 비밀번호 확인 검사
    const validateConfirmPassword = (confirmPassword) => {
        if (confirmPassword.length === 0) {
            setValidation(prev => ({
                ...prev,
                confirmPassword: { isValid: false, message: '' }
            }));
            return;
        }

        const isValid = confirmPassword === formData.password;

        setValidation(prev => ({
            ...prev,
            confirmPassword: {
                isValid,
                message: isValid ? '비밀번호가 일치합니다.' : '비밀번호가 일치하지 않습니다.'
            }
        }));
    };

    // 아이디 중복 확인
    const handleCheckLoginId = async () => {
        if (!formData.loginId.trim()) {
            showError('아이디를 입력해주세요.');
            return;
        }

        try {
            const response = await fetch(`http://localhost:8080/api/auth/check/userid?loginId=${formData.loginId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (response.ok) {
                setValidation(prev => ({
                    ...prev,
                    loginId: {
                        isValid: !data.exists,
                        message: data.message
                    }
                }));
            } else {
                showError('아이디 중복 확인에 실패했습니다.');
            }
        } catch (error) {
            console.error('아이디 중복 확인 실패:', error);
            showError('서버 연결에 실패했습니다.');
        }
    };

    // 이메일 인증번호 발송
    const handleSendEmail = async () => {
        if (!formData.email.trim()) {
            showError('이메일을 입력해주세요.');
            return;
        }

        try {
            const response = await fetch(`http://localhost:8080/api/auth/email/send`, {
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

    // 인증번호 재전송
    const handleResendEmail = () => {
        setTimeLeft(0);
        setIsEmailSent(false);
        setFormData(prev => ({ ...prev, verificationCode: '' }));
        handleSendEmail();
    };

    // 이메일 인증번호 확인
    const handleVerifyEmail = async () => {
        if (!formData.verificationCode.trim()) {
            showError('인증번호를 입력해주세요.');
            return;
        }

        if (timeLeft <= 0) {
            showError('인증번호가 만료되었습니다. 다시 요청해주세요.');
            return;
        }

        try {
            const response = await fetch(`http://localhost:8080/api/auth/email/verify`, {
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
                setTimeLeft(0); // 타이머 정지
            } else {
                showError(data.message || '인증번호가 올바르지 않습니다.');
            }
        } catch (error) {
            console.error('인증번호 확인 실패:', error);
            showError('서버 연결에 실패했습니다.');
        }
    };

    // 회원가입 처리
    const handleSignup = async (e) => {
        e.preventDefault();

        // 유효성 검사
        if (!validation.loginId.isValid) {
            showError('아이디 중복 확인을 해주세요.');
            return;
        }
        if (formData.password.length < 8 || formData.password.length > 16) {
            showError('비밀번호는 8~16자여야 합니다.');
            return;
        }
        if (!validation.confirmPassword.isValid) {
            showError('비밀번호가 일치하지 않습니다.');
            return;
        }
        if (!isEmailVerified) {
            showError('이메일 인증을 완료해주세요.');
            return;
        }
        if (!formData.userName.trim()) {
            showError('이름을 입력해주세요.');
            return;
        }

        try {
            const response = await fetch(`http://localhost:8080/api/auth/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    loginId: formData.loginId,
                    password: formData.password,
                    userName: formData.userName,
                    email: formData.email
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                navigate('/welcome', {
                    state: {
                        userName: formData.userName,
                        fromSignup: true  //회원가입을 통한 접근
                    },
                    replace: true  // 뒤로가기 방지
                });
            } else {
                showError(data.message || '회원가입에 실패했습니다.');
            }
        } catch (error) {
            console.error('회원가입 실패:', error);
            showError('서버 연결에 실패했습니다.');
        }
    };

  return (
    <div className="app-container">
      <SignupHeader />
      <main className="content-area signup-con">
        <form className="signup-form" onSubmit={handleSignup}>

            {/*아이디 입력 - 중복확인*/}
          <div className="form-control-con">
            <div className="input-group-custom">
              <input type="text" name="loginId" className="form-control flex-grow-1" placeholder="아이디" value={formData.loginId} onChange={handleChange}/>
              <button type="button" className="btn btn-custom" onClick={handleCheckLoginId}>중복확인</button>
            </div>
              {validation.loginId.message && (
                  <div className={`form-text-${validation.loginId.isValid ? 'valid' : 'invalid'} fw-semibold`}>
                      * {validation.loginId.message}
                  </div>
              )}
          </div>


            {/*비밀번호 입력*/}
          <div className="form-control-con">
            <input type="password" name="password" className="form-control" placeholder="비밀번호" value={formData.password} onChange={handleChange}/>
              {validation.password.message && (
                  <div className={`form-text-${validation.password.isValid ? 'valid' : 'invalid'} fw-semibold`}>
                      * {validation.password.message}
                  </div>
              )}
          </div>

            {/*비밀번호 확인하기*/}
          <div className="form-control-con">
            <input type="password" name="confirmPassword" className="form-control" placeholder="비밀번호 확인" value={formData.confirmPassword} onChange={handleChange}/>
              {formData.confirmPassword && (
                  <div className={`form-text-${validation.confirmPassword.isValid ? 'valid' : 'invalid'} fw-semibold`}>
                      * {validation.confirmPassword.message}
                  </div>
              )}
          </div>

          <div className="form-control-con">
            <input type="text" name="userName" className="form-control" placeholder="이름" value={formData.userName} onChange={handleChange}/>
          </div>

            {/*// 1단계: 이메일 + 인증번호 받기 버튼*/}
          <div className="form-control-con ">
              <div className="input-group-custom">
            <input type="email" name="email" className="form-control" placeholder="이메일" value={formData.email} onChange={handleChange} disabled={isEmailVerified}/>
            <button type="button" className="btn btn-custom" onClick={handleSendEmail} disabled={isEmailVerified || timeLeft > 0}>인증번호 받기</button>
              </div>

          </div>

            {/*//2단계 인증번호 입력하고 + 인증번호 확인하는 버튼*/}
          <div className="form-control-con input-group-custom">
            <input type="text" name="verificationCode" className="form-control flex-grow-1" placeholder="인증번호 입력하세요." value={formData.verificationCode} onChange={handleChange} disabled={isEmailVerified || timeLeft <= 0}/>
              <button type="button" className="btn btn-custom" onClick={handleVerifyEmail} disabled={isEmailVerified || timeLeft <= 0}>인증하기</button>
          </div>

            {/* 타이머 및 재전송 (이메일 전송 후에만) */}
            {isEmailSent && (
                <div className="form-control-con">
                    {timeLeft > 0 && !isEmailVerified ? (
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
                    ) : timeLeft === 0 && !isEmailVerified ? (
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
                    ) : isEmailVerified ? (
                        <div className="form-text-valid fw-semibold">
                            * 이메일 인증이 완료되었습니다.
                        </div>
                    ) : null}
                </div>
            )}

            {error && (
                <div className="alert alert-danger mb-3" role="alert">
                    {error}
                </div>
            )}

            <button type="submit" className="btn btn-login" onClick={handleSignup}>회원가입</button>
        </form>
      </main>
      <div className="spacer"></div>
    </div>
  );
}

export default SignupPage;
