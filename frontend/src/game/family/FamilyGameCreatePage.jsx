import React from 'react';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';
import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';
import AlarmModal from '@/components/modal/AlarmModal';

function FamilyGameCreatePage() {
  return (
    <div className="app-container d-flex flex-column">
      <FamilyHeader />

      <main className="content-area family-con">
        <div className="menu-title">
          <div>게임 만들기</div>
          <div className="progress">
            <div
              className="progress-bar"
              role="progressbar"
              style={{ width: '60%' }}
              aria-valuenow="6"
              aria-valuemin="0"
              aria-valuemax="10"
            ></div>
            <div className="progress-label">6 / 10</div>
          </div>
        </div>

        <form className="signup-form game-signup-form">
          <div className="form-control-con">
            <input
              type="text"
              className="form-control"
              placeholder="게임 제목을 입력하세요."
            />
          </div>

          <div className="form-control-con">
            <div className="form-control game-file-desc-con">
              <div className="game-file-desc mb-3 mt-2">
                게임에 사용할 사진을 업로드하세요.
              </div>
              <button className="btn btn-add" type="button">파일 선택</button>
            </div>
          </div>

          <div className="form-control-con">
            <input
              type="text"
              className="form-control"
              placeholder="정답 단어를 입력하세요."
            />
          </div>

          <div className="form-control-con">
            <textarea
              className="form-control"
              placeholder="설명을 입력하세요."
            ></textarea>
          </div>

          <button type="button" className="btn btn-login">
            다음 문제 추가하기
          </button>
          <button type="submit" className="btn btn-login">
            게임 생성완료
          </button>
        </form>
      </main>

      <AlarmModal />
      <FamilyFooter />
    </div>
  );
}

export default FamilyGameCreatePage;
