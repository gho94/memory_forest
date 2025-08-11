import { BrowserRouter, Routes, Route } from 'react-router-dom';

import LoginPage from '@/user/family/LoginPage';
import FindIdPage from '@/user/family/FindIdPage';
import SignupPage from '@/user/family/SignupPage';
import FindPwPage from '@/user/family/FindPwPage';
import ResetPwPage from '@/user/family/ResetPwPage';
import WelcomePage from '@/user/family/WelcomePage';

import FamilyDashboardPage from '@/user/family/FamilyDashboardPage';
import PatientProfilePage from '@/user/family/PatientProfilePage';
import PatientDetailPage from '@/user/family/PatientDetailPage';
import FamilyGameCreatePage from '@/game/family/FamilyGameCreatePage';
import FamilyGameCompletePage from '@/game/family/FamilyGameCompletePage';
import FamilyGameListPage from '@/game/family/FamilyGameListPage';

import PatientDashboardPage from '@/game/patient/PatientDashboardPage';
import PatientChartPage from '@/user/patient/PatientChartPage';
import PatientMyPage from '@/user/patient/PatientMyPage';
import PatientRecord from '@/user/patient/PatientRecord';
import GamePage from '@/game/patient/GamePage';
import CommonCodePage from '@/user/common/CommonCodePage';

function Router() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 로그인 - 회원가입 / 아이디 찾기 각각 페이지 연결  */}
        <Route path="/" element={<LoginPage />} />
        <Route path="/findId" element={<FindIdPage />} />
        <Route path="/signup" element={<SignupPage />} />
          <Route path="/findPw" element={<FindPwPage />} />
          <Route path="/resetPw" element={<ResetPwPage />} />
          <Route path="/welcome" element={<WelcomePage />} />
        {/* 비밀번호 찾기 추가 필요함 - 백엔드 개발 진행하면서 만들게여 */}

        {/* 동행자 */}
        <Route path="/companion/dashboard" element={<FamilyDashboardPage />} />
        <Route path="/companion/profileadd" element={<PatientProfilePage />} />
        <Route path="/companion/detail" element={<PatientDetailPage />} />
        {/* 동행자-게임 */}
        <Route path="/companion/games/create" element={<FamilyGameCreatePage />} />
        <Route path="/companion/games/complete" element={<FamilyGameCompletePage />} />
        <Route path="/companion/games/list" element={<FamilyGameListPage />} />
        
        {/* 기록자 */}
        <Route path="/recorder/dashboard" element={<PatientDashboardPage />} />
        <Route path="/recorder/chart" element={<PatientChartPage />} />
        <Route path="/recorder/mypage" element={<PatientMyPage />} />
        <Route path="/recorder/record/create" element={<PatientRecord />} />
        <Route path="/recorder/record/list" element={<PatientRecord />} />
        {/* 기록자-게임 */}
        <Route path="/recorder/game" element={<GamePage />} />

        {/* 기타 관리자.. 추가예쩡 */}
        <Route path="/common-code" element={<CommonCodePage />} />

      </Routes>
    </BrowserRouter>
  );
}

export default Router;
