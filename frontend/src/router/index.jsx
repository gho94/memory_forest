import { BrowserRouter, Routes, Route } from 'react-router-dom';

import LoginPage from '../user/family/LoginPage';
import FindIdPage from '../user/family/FindIdPage';
import SignupPage from '../user/family/SignupPage';

import FamilyDashboardPage from '../user/family/FamilyDashboardPage';
import PatientProfilePage from '../user/family/PatientProfilePage';
import PatientDetailPage from '../user/family/PatientDetailPage';
import FamilyGameCreatePage from '../game/family/FamilyGameCreatePage';
import FamilyGameCompletePage from '../game/family/FamilyGameCompletePage';
import FamilyGameListPage from '../game/family/FamilyGameListPage';

import PatientDashboardPage from '../game/patient/PatientDashboardPage';
import PatientChartPage from '../user/patient/PatientChartPage';
import PatientMyPage from '../user/patient/PatientMyPage';
import PatientRecord from '../user/patient/PatientRecord';
import GamePage from '../game/patient/GamePage';
import GameResultPage from '../game/patient/GameResultPage';
import PatientGameAnswerResultPage from '../game/patient/PatientGameAnswerResultPage';

function Router() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 로그인 - 회원가입 / 아이디 찾기 각각 페이지 연결  */}
        <Route path="/" element={<LoginPage />} />
        <Route path="/findId" element={<FindIdPage />} />
        <Route path="/signup" element={<SignupPage />} />
        {/* 비밀번호 찾기 추가 필요함 - 백엔드 개발 진행하면서 만들게여 */}

        {/* 동행자 */}
        <Route path="/guardian/dashboard" element={<FamilyDashboardPage />} />
        <Route path="/guardian/profileadd" element={<PatientProfilePage />} />
        <Route path="/guardian/detail" element={<PatientDetailPage />} />
        {/* 동행자-게임 */}
        <Route path="/guardian/games/create" element={<FamilyGameCreatePage />} />
        <Route path="/guardian/games/complete" element={<FamilyGameCompletePage />} />
         <Route path="/guardian/games/list" element={<FamilyGameListPage />} />
        
        {/* 기록자 */}
        <Route path="/recoder/dashboard" element={<PatientDashboardPage />} />
        <Route path="/recoder/chart" element={<PatientChartPage />} />
        <Route path="/recoder/mypage" element={<PatientMyPage />} />
        <Route path="/recoder/record" element={<PatientRecord />} />
        {/* 기록자-게임 */}
        <Route path="/recoder/game" element={<GamePage />} />
        <Route path="/recoder/game/result" element={<GameResultPage />} />
        <Route path="/recoder/game/result" element={<PatientGameAnswerResultPage/>} />


        {/* 기타 관리자.. 추가예쩡 */}

      </Routes>
    </BrowserRouter>
  );
}

export default Router;
