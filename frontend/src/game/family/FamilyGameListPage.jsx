import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';
import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';
import AlarmModal from '@/components/modal/AlarmModal';

function FamilyGameListPage() {
  return (
    <div className="app-container d-flex flex-column">
      <FamilyHeader />

      <main className="content-area family-con">
        <div className="menu-title">
          <div>게임 리스트</div>
        </div>

        <div className="game-list-wrap">
          <div className="game-list-con">
            {[1, 2, 3].map((num) => (
              <div key={num} className="game-item">
                <div className="game-number">{num}</div>
                <div className="game-box">
                  <div className="game-img" />
                  <div className="game-texts">
                    <div className="game-title">제목임둥</div>
                    <div className="game-answer">정답 : 너구리</div>
                  </div>
                  <button className="game-edit-btn">수정</button>
                </div>
              </div>
            ))}
          </div>

          <button type="button" className="btn btn-login mt-4">목록으로</button>
        </div>
      </main>

      <AlarmModal />

      <FamilyFooter />
    </div>
  );
}

export default FamilyGameListPage;
