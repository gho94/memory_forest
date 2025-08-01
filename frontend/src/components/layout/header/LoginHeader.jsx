import '@/assets/css/common.css';

function LoginHeader({ title = '아이디 찾기' }) {
  return (
    <header className="app-header utility-header">
      <div className="back-btn" role="button" aria-label="뒤로가기"></div>
      <div className="center-group">
        <div className="logo" aria-label="기억 숲 로고"></div>
        <div className="title">{title}</div>
      </div>
    </header>
  );
}

export default LoginHeader;