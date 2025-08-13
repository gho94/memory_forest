import React from 'react';
import '@/assets/css/common.css';
import '@/assets/css/patient.css';
import PatientHeader from '@/components/layout/header/PatientHeader';
import PatientFooter from '@/components/layout/footer/PatientFooter';
import GamePlayerChartItem from '@/components/game/GamePlayerChartItem';
import GamePlayerChartStatsItem from '@/components/game/GamePlayerChartStatsItem';
import { useChartDataLogic } from '@/hooks/game/common/useChartDataLogic';
import { useChartState } from '@/hooks/game/patient/useChartState';

function PatientChartPage() {
  // URL에서 gameId 추출
  const queryParams = new URLSearchParams(location.search);
  const gameIdFromUrl = queryParams.get('gameId');
  const showToggleButton = !!gameIdFromUrl;

  // 커스텀 훅으로 상태 및 로직 관리
  const {
    includeGameId,
    dashboardData,
    statsData,
    loading,
    handleToggleGameId
  } = useChartState(gameIdFromUrl);

  // 차트 데이터 변환
  const chartData = useChartDataLogic(dashboardData);

  return (
      <div className="app-container d-flex flex-column">
        <PatientHeader />
        <main className="content-area patient-con game-result-area">
          <div className="greeting">나의 진행도</div>

          <GamePlayerChartItem
              loading={loading}
              chartData={chartData}
              includeGameId={includeGameId}
              showToggleButton={showToggleButton}
              onToggleGameId={handleToggleGameId}
          />

          <GamePlayerChartStatsItem
              loading={loading}
              statsData={statsData}
          />
        </main>
        <PatientFooter />
      </div>
  );
}

export default PatientChartPage;