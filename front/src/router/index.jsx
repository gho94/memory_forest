import { BrowserRouter, Routes, Route } from 'react-router-dom';

import LoginPage from '../user/family/LoginPage';
import SignupPage from '../user/family/SignupPage';
import FindIdPage from '../user/family/FindIdPage';
import PatientProfilePage from '../user/family/PatientProfilePage';
import FamilyGameListPage from '../game/family/FamilyGameListPage';
import FamilyGameCompletePage from '../game/family/FamilyGameCompletePage';

import GamePage from '../game/patient/GamePage';
import GameResultPage from '../game/patient/GameResultPage';
import PatientDashboardPage from '../game/patient/PatientDashboardPage';
import PatientChartPage from '../user/patient/PatientChartPage';
import PatientMyPage from '../user/patient/PatientMyPage';
import PatientRecord from '../user/patient/PatientRecord';

function Router() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 로그인 - 회원가입 / 아이디 찾기 각각 페이지 연결  */}
        <Route path="/" element={<LoginPage />} />
        <Route path="/findId" element={<FindIdPage />} />
        <Route path="/signup" element={<SignupPage />} />


        {/*  */}
        <Route path="/profile" element={<PatientProfilePage />} />
        <Route path="/family/games" element={<FamilyGameListPage />} />
        <Route path="/family/games/complete" element={<FamilyGameCompletePage />} />


        {/* 환자 게임 화면 -  */}
        <Route path="/patient/game" element={<GamePage />} />
        <Route path="/patient/game/result" element={<GameResultPage />} />
        <Route path="/patient/dashboard" element={<PatientDashboardPage />} />
        <Route path="/patient/chart" element={<PatientChartPage />} />
        <Route path="/patient/mypage" element={<PatientMyPage />} />
        <Route path="/patient/record" element={<PatientRecord />} />

        {/* 기타 관리자.. 추가예쩡 */}
      </Routes>
    </BrowserRouter>
  );
}

export default Router;
