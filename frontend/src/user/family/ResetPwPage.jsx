import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import LoginHeader from '@/components/layout/header/LoginHeader';
import '@/assets/css/common.css';
import '@/assets/css/login.css';

function ResetPasswordPage() {

    const navigate = useNavigate();
    const location = useLocation();

    const [formData, setFormData] = useState({
        newPassword: '',
        confirmPassword: ''
    });

    const [validation, setValidation] = useState({
        newPassword: { isValid: false, message: '' },
        confirmPassword: { isValid: false, message: '' }
    });

    const [isPasswordReset, setIsPasswordReset] = useState(false);
    const [error, setError] = useState('');

    // 이전 페이지에서 전달받은 인증 정보
    const authInfo = location.state;
    
    //삭제
    useEffect(() => {
        console.log("=== ResetPasswordPage authInfo 확인 ===");
        console.log("location.state:", location.state);
        console.log("authInfo:", authInfo);
        console.log("authInfo?.loginId:", authInfo?.loginId);
        console.log("authInfo?.email:", authInfo?.email);
        console.log("authInfo?.verificationCode:", authInfo?.verificationCode);
    }, [authInfo, location.state]);

    //에러 메세지...아아ㅏㅏㅏㅏㅏㅏ
    const showError = (message) => {
        setError(message);
        if (message) {
            setTimeout(() => {
                setError('');
            }, 5000);
        }
    };

    // 인증되지 않은 접근 차단
    useEffect(() => {
        if (!authInfo || !authInfo.verified) {
          navigate('/findPw',{ replace: true });
        }
    }, [authInfo, navigate]);

    // 비밀번호 변경 완료 후 뒤로가기 방지
    useEffect(() => {
        if (isPasswordReset) {
            const handlePopState = (e) => {
                e.preventDefault();
                navigate('/', { replace: true });
            };
            window.addEventListener('popstate', handlePopState);
            window.history.pushState(null, '', window.location.pathname);

            return () => {
                window.removeEventListener('popstate', handlePopState);
            };
        }
    }, [isPasswordReset, navigate]);


    // if (!authInfo?.verified) navigate('/findPw');

    // 입력값 변경 핸들러
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));

        // 비밀번호 실시간 검증
        if (name === 'newPassword') {
            validatePassword(value);
        } else if (name === 'confirmPassword') {
            validateConfirmPassword(value);
        }
    };

    // 비밀번호 간단 유효성 검사
    const validatePassword = (password) => {
        if (password.length === 0) {
            setValidation(prev => ({
                ...prev,
                newPassword: { isValid: false, message: '' }
            }));
            return;
        }

        const isValid = password.length >= 8 && password.length <= 16;
        const message = isValid
            ? '올바른 비밀번호입니다.'
            : '8~16자의 영문/대소문자, 숫자, 특수문자를 사용해 주세요.';

        setValidation(prev => ({
            ...prev,
            newPassword: { isValid, message }
        }));
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

        const isValid = confirmPassword === formData.newPassword;
        const message = isValid ? '비밀번호가 일치합니다.' : '비밀번호가 일치하지 않습니다.';

        setValidation(prev => ({
            ...prev,
            confirmPassword: { isValid, message }
        }));
    };

    // 비밀번호 재설정 완료
    const handleResetPassword = async (e) => {
        e.preventDefault();

        if (!validation.newPassword.isValid) {
            showError('비밀번호 형식을 확인해주세요.');
            return;
        }

        if (!validation.confirmPassword.isValid) {
            showError('비밀번호가 일치하지 않습니다.');
            return;
        }

        try {
            const response = await fetch(`${window.API_BASE_URL}/api/auth/password/reset/complete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    loginId: authInfo?.loginId,
                    email: authInfo?.email,
                    code: authInfo?.verificationCode,
                    newPassword: formData.newPassword,
                    confirmPassword: formData.confirmPassword
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                setIsPasswordReset(true);
                // alert('비밀번호가 성공적으로 변경되었습니다!');

                // 성공 후 폼 데이터 클리어 -> 추가하면 좋을거 같아서 찾아서 넣음
                setFormData({ newPassword: '', confirmPassword: '' });
                setValidation({
                    newPassword: { isValid: false, message: '' },
                    confirmPassword: { isValid: false, message: '' }
                });

            } else {
                showError(data.message || '비밀번호 변경에 실패했습니다.');
            }
        } catch (error) {
            console.error('비밀번호 변경 실패:', error);
            showError('서버 연결에 실패했습니다.');
        }
    };

    // 로그인 페이지로 이동
    const goToLogin = () => {
        // alert('로그인 페이지로 이동합니다.');
        navigate('/', { replace: true }); // 새로고침 시 안전하게 리다이렉트
    };

    return (
        <div className="app-container">
            <LoginHeader title={isPasswordReset ? "비밀번호 변경 완료" : "비밀번호 재설정"} />

            <main className="content-area signup-con">
                <div className="find-id-form">

                    {/* 비밀번호 재설정할 사람에 대해서 ... 내용 띄우는거  */}
                    {!isPasswordReset && (
                    <div className="user-information">
                        <div className="text3"><strong>{authInfo?.loginId || 'USER'}</strong> 계정의 비밀번호를 재설정합니다.</div>
                    </div>
                    )}


                    {!isPasswordReset ? (
                        <>
                            <div className="form-control-con">
                                <input
                                    type="password"
                                    name="newPassword"
                                    className="form-control"
                                    placeholder="새 비밀번호"
                                    value={formData.newPassword}
                                    onChange={handleChange}
                                />
                                {validation.newPassword.message && (
                                    <div className={`form-text-${validation.newPassword.isValid ? 'valid' : 'info'} fw-semibold`}>
                                        * {validation.newPassword.message}
                                    </div>
                                )}
                                {!validation.newPassword.message && formData.newPassword === '' && (
                                    <div className="form-text-info fw-semibold">
                                    </div>
                                )}
                            </div>

                            <div className="form-control-con">
                                <input
                                    type="password"
                                    name="confirmPassword"
                                    className="form-control"
                                    placeholder="새 비밀번호 확인"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                />
                                {formData.confirmPassword && validation.confirmPassword.message && (
                                    <div className={`form-text-${validation.confirmPassword.isValid ? 'valid' : 'invalid'} fw-semibold`}>
                                        * {validation.confirmPassword.message}
                                    </div>
                                )}
                            </div>

                            {/* 에러 메시지 */}
                            {error && (
                                <div className="alert alert-danger mb-3" role="alert">
                                    {error}
                                </div>
                            )}
                            <button
                                type="submit"
                                className="btn btn-login"
                                onClick={handleResetPassword}
                            >
                                비밀번호 변경
                            </button>
                        </>
                    ) : (
                        <>
                            <div className="password-reset-result" >
                                <div className="text2">비밀번호 변경이 완료되었습니다.</div>
                                <div className="text3">새로운 비밀번호로 로그인해주세요.</div>
                            </div>
                            <button type="button" className="btn btn-login" onClick={goToLogin}>로그인</button>
                        </>
                    )}

                </div>
            </main>

            <div className="spacer"></div>
        </div>
    );
}

export default ResetPasswordPage;