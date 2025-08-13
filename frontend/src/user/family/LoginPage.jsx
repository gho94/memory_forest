import { useState } from 'react';
import { useNavigate,Link } from 'react-router-dom';
import '@/assets/css/common.css';
import '@/assets/css/patient.css';
import '@/assets/css/login.css';
import '@/assets/css/test.css';

function LoginPage() {

    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        loginId: '',
        password: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    // console.log('-------------------test---------------------);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        if (error) setError('');
    };


    ////localStorage 대신에 SessionStorage 으로 수정
    const handleLogin = async (loginId, password) => {
        setLoading(true);
        setError('');

        try {
            const response = await fetch(`http://localhost:8080/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include', // 세션 쿠키 포함
                body: JSON.stringify({
                    loginId: loginId,
                    password: password
                })
            });

            console.log('응답 상태:', response.status);

            const data = await response.json();
            console.log('받은 데이터:', data);

            if (response.ok && data.success) {
                console.log('로그인 성공:', data);
                console.log(`로그인 성공! 환영합니다, ${data.userName}님!`);

                if (data.userTypeCode === 'A20002') { //COMPANION == A20002
                    navigate('/companion/dashboard');
                } else if (data.userTypeCode === 'A20001') { //RECORDER == A20001
                    navigate('/recorder/dashboard');
                } else {
                    navigate('/companion/dashboard'); // 기본값
                }
            } else {
                setError(data.message || '로그인에 실패했습니다.');
            }
        } catch (error) {
            console.error('로그인 실패:', error);
            setError('서버와의 연결에 실패했습니다. 잠시 후 다시 시도해주세요.');
        } finally {
            setLoading(false);
        }
    };

    // 소셜 로그인
    const handleSocialLogin = (provider) => {
        // Spring Security OAuth2 엔드포인트로 직접 리다이렉트 처리하기
        window.location.href = `http://localhost:8080/oauth2/authorization/${provider}`;
    };


    // 폼 제출 처리
    const handleSubmit = (e) => {
        e.preventDefault();

        if (!formData.loginId.trim()) {
            setError('아이디를 입력해주세요.');
            return;
        }
        if (!formData.password.trim()) {
            setError('비밀번호를 입력해주세요.');
            return;
        }

        handleLogin(formData.loginId, formData.password);
    };

  return (
    <div className="app-container login-container d-flex flex-column">
      <main className="content-area login-con">
        <div className="logo-con">
          <div className="logo" role="img" aria-label="기억 숲 아이콘"></div>
        </div>
        <div className="login-title">로그인</div>

        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <input type="text" name="loginId" className="form-control" placeholder="아이디" value={formData.loginId} onChange={handleChange} disabled={loading}/>
          </div>
          <div className="mb-4">
            <input type="password" name="password" className="form-control" placeholder="비밀번호" value={formData.password} onChange={handleChange} disabled={loading}/>
          </div>

            {error && (
                <div className="alert alert-danger mb-3" role="alert">
                    {error}
                </div>
            )}

          <button type="submit" className="btn btn-login" disabled={loading} onClick={handleSubmit}>{loading ? '로그인 중...' : '로그인'}</button>
        </form>

        <div className="login-links">
          <Link to="/findId">아이디 찾기</Link>
          <Link to="/findPw">비밀번호 찾기</Link>
          <Link to="/signup">회원가입</Link>
        </div>


          {/* 소셜 로그인 버튼들 */}
          <div className="social-login-section">
              <button
                  type="button"
                  className="btn btn-naver mb-2"
                  onClick={() => handleSocialLogin('naver')}
                  disabled={loading}
              >
                  <span className="naver-icon">N</span>
                  네이버로 로그인
              </button>

              <button
                  type="button"
                  className="btn btn-kakao mb-2"
                  onClick={() => handleSocialLogin('kakao')}
                  disabled={loading}
              >
                  <span className="kakao-icon">K</span>
                  카카오로 로그인
              </button>
          </div>




      </main>
    </div>
  );
}

export default LoginPage;
