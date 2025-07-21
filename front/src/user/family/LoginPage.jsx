import '../../assets/css/common.css';
import '../../assets/css/patient.css';
import '../../assets/css/login.css';

function LoginPage() {
  return (
    <div className="app-container login-container d-flex flex-column">
      <main className="content-area login-con">
        <div className="logo-con">
          <div className="logo" role="img" aria-label="기억 숲 아이콘"></div>
        </div>
        <div className="login-title">로그인</div>

        <form>
          <div className="mb-3">
            <input type="text" className="form-control" placeholder="아이디" />
          </div>
          <div className="mb-4">
            <input type="password" className="form-control" placeholder="비밀번호" />
          </div>
          <button type="submit" className="btn btn-login">로그인</button>
        </form>

        <div className="login-links">
          <a href="#">아이디 찾기</a>
          <a href="#">비밀번호 찾기</a>
          <a href="#">회원가입</a>
        </div>
      </main>
    </div>
  );
}

export default LoginPage;
