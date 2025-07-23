import '../../assets/css/common.css';
import '../../assets/css/login.css';
import '../../assets/css/family.css';
import FamilyHeader from '../../components/layout/header/FamilyHeader';
import FamilyFooter from '../../components/layout/footer/FamilyFooter';
import AlarmModal from '../../components/modal/AlarmModal';

function FamilyGameCompletePage() {
  return (
    <div className="app-container d-flex flex-column">
      <FamilyHeader />

      <main className="content-area family-con center">
        <div className="game-result-title">게임 생성 완료!</div>

        <div className="signup-form game-signup-form game-complete-gap">
          <div className="row game-result-con">
            <div className="col-5 desc-title">게임 제목</div>
            <div className="col-7">untitled10</div>
            <div className="col-5 desc-title">문제 개수</div>
            <div className="col-7">10</div>
          </div>

          <div>
            <div className="game-result-share-text">게임 공유하기</div>
            <div className="game-result-share-icon mt-3 row">
              <div className="col-6 kakaotalk-icon"></div>
              <div className="col-6 link-icon"></div>
            </div>
          </div>

          <button type="button" className="btn btn-login mt-4">목록으로</button>
        </div>
      </main>

      <AlarmModal />

      <FamilyFooter />
    </div>
  );
}

export default FamilyGameCompletePage;
