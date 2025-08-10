import { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import LoginHeader from '@/components/layout/header/LoginHeader';

function WelcomePage() {
    const navigate = useNavigate();
    const location = useLocation();
    const [userName, setUserName] = useState('');

    useEffect(() => {//회원가입을 통해서만 접근 가능
        if (!location.state?.userName || !location.state?.fromSignup) {// 직접 접근하거나 새로고침한 경우 로그인 페이지로 리디렉션
            navigate('/', { replace: true });
            return;
        }
        setUserName(location.state.userName);
    }, [location.state, navigate]);


    const GoToLogin = () => {
        navigate('/');
    };

    return (
        <div className="app-container welcome-page">
            <LoginHeader title="환영합니다" />
            <main className="content-area">
                <div className="signup-form welcome-container">
                    <div className={`welcome-emoji`}>🎉</div>
                    <div className="welcome-title">회원가입을 축하드립니다!</div>
                    <div className="welcome-message">안녕하세요, <span className="welcome-username">{userName}</span>님!<br/>기억숲의 새로운 동행자가 되어주셔서 감사합니다.</div>
                    <div className="welcome-branding">🌲 이제 소중한 추억들을 기억숲에서<br/>기록자를 추가해 함께해보세요.</div>

                    <button type="button" className="btn btn-login" onClick={GoToLogin}>로그인하러 가기</button>
                </div>
            </main>
            <div className="spacer"></div>
        </div>
    );
}
export default WelcomePage;