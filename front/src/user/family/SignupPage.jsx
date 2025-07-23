import '../../assets/css/common.css';  
import '../../assets/css/login.css'; 
import SignupHeader from '../../components/layout/header/SignupHeader';

function SignupPage() {
  return (
    <div className="app-container">
      <SignupHeader />
      <main className="content-area signup-con">
        <form className="signup-form">
          <div className="form-control-con">
            <div className="input-group-custom">
              <input type="text" className="form-control flex-grow-1" placeholder="아이디" />
              <button type="button" className="btn btn-custom">중복확인</button>
            </div>
            <div className="form-text-valid fw-semibold">* 사용가능한 아이디입니다.</div>
          </div>
          <div className="form-control-con">
            <input type="password" className="form-control" placeholder="비밀번호" />
            <div className="form-text-valid fw-semibold">
              * 8~16자의 영문/대소문자, 숫자, 특수문자를 사용해 주세요.
            </div>
          </div>
          <div className="form-control-con">
            <input type="password" className="form-control" placeholder="비밀번호 확인" />
            <div className="form-text-invalid fw-semibold">* 비밀번호가 일치하지 않습니다.</div>
          </div>
          <div className="form-control-con">
            <input type="text" className="form-control" placeholder="이름" />
          </div>
          <div className="form-control-con">
            <input type="email" className="form-control" placeholder="이메일" />
          </div>
          <div className="form-control-con input-group-custom">
            <input type="text" className="form-control flex-grow-1" placeholder="인증번호 입력하세요." />
            <button type="button" className="btn btn-custom">인증</button>
          </div>
          <button type="submit" className="btn btn-login">회원가입</button>
        </form>
      </main>
      <div className="spacer"></div>
    </div>
  );
}

export default SignupPage;
