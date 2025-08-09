import React from 'react';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';
import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';
import AlarmModal from '@/components/modal/AlarmModal';
import GamePlayerStatItem from '@/components/game/GamePlayerStatItem';
import GamePlayerDatePickerItem from '@/components/game/GamePlayerDatePickerItem';
import GamePlayerChartAndGameItem from '@/components/game/GamePlayerChartAndGameItem';
import { usePatientDashboardLogic } from '@/hooks/game/usePatientDashboardLogic';
import { useChartDataLogic } from '@/hooks/game/useChartDataLogic';
import { usePDFGenerator } from '@/hooks/game/usePDFGenerator';

function PatientDetailPage() {
  const {
    dashboardData,
    loading,
    startDate,
    endDate,
    setStartDate,
    setEndDate,
    handleSearch
  } = usePatientDashboardLogic();

  const chartData = useChartDataLogic(dashboardData);
  const { handlePrintToPDF } = usePDFGenerator();

  const { stats, gameList, searchDate } = dashboardData || {};

  return (
      <div className="app-container d-flex flex-column">
        <FamilyHeader />
        <main className="content-area guardian-con">
          <div className="detail-title">
            <div><span>환자 01</span> 최근 활동</div>
            <div>
              <div className="icon-btn print-btn" onClick={handlePrintToPDF}></div>
              <div className="icon-btn trash-btn"></div>
            </div>
          </div>

          {/* 통계 영역 */}
          <GamePlayerStatItem stats={stats} loading={loading.stats} />

          {/* 날짜 선택기 */}
          <GamePlayerDatePickerItem
              startDate={startDate}
              endDate={endDate}
              setStartDate={setStartDate}
              setEndDate={setEndDate}
              handleSearch={handleSearch}
          />

          {/* 차트 및 게임 결과 */}
          <GamePlayerChartAndGameItem
              chartData={chartData}
              loading={loading}
              searchDate={searchDate}
              gameList={gameList}
          />
        </main>

        <AlarmModal />
        <FamilyFooter />
      </div>
  );
}

export default PatientDetailPage;