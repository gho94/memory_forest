import '../../assets/css/common.css';
import '../../assets/css/login.css';
import LoginHeader from '../../components/layout/header/LoginHeader';

function FindIdPage() {
  return (
    <div className="app-container">
      <LoginHeader title="아이디 찾기" />

      <main className="content-area signup-con">
        <form className="find-id-form">
          {/* 이메일 입력 + 인증번호 전송 버튼 */}
          <div>
            <div className="input-group-custom">
              <input
                type="text"
                className="form-control flex-grow-1"
                placeholder="이메일"
              />
              <button type="button" className="btn btn-custom">
                인증번호
              </button>
            </div>
          </div>

          {/* 인증번호 입력 */}
          <div>
            <input
              type="text"
              className="form-control"
              placeholder="인증번호를 입력하세요."
            />
          </div>

          {/* 아이디 찾기 결과 (초기에는 숨김 처리) */}
          <div style={{ display: 'none' }} className="find-id-result-con">
            가입하신 아이디는<br />
            [<span className="id-result">test1234</span>] 입니다.
          </div>

          {/* 아이디 찾기 버튼 */}
          <button type="submit" className="btn btn-login">
            아이디 찾기
          </button>
        </form>
      </main>

      <div className="spacer"></div>
    </div>
  );
}

export default FindIdPage;
