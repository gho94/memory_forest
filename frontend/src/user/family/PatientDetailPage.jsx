import React, { useState } from 'react';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';
import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';
import AlarmModal from '@/components/modal/AlarmModal';
import GamePlayerStatItem from '@/components/game/GamePlayerStatItem';
import GamePlayerDatePickerItem from '@/components/game/GamePlayerDatePickerItem';
import GamePlayerChartAndGameItem from '@/components/game/GamePlayerChartAndGameItem';
import RecordChartAndDataItem from '@/components/record/RecordChartAndDataItem'; // 새로운 기록용 컴포넌트
import { usePatientDashboardLogic } from '@/hooks/game/family/usePatientDashboardLogic';
import { usePatientRecordLogic } from '@/hooks/record/family/usePatientRecordLogic'; // 새로운 기록용 훅
import { useChartDataLogic } from '@/hooks/game/common/useChartDataLogic';
import { useRecordChartDataLogic } from '@/hooks/record/family/useRecordChartDataLogic'; // 새로운 기록용 차트 훅
import { usePDFGenerator } from '@/hooks/game/family/usePDFGenerator';
import RecordStatItem from "@/components/record/RecordStatItem";

function PatientDetailPage() {
  const [activeTab, setActiveTab] = useState('game'); // 'game' or 'record'

  // 게임 관련 로직
  const {
    dashboardData: gameDashboardData,
    loading: gameLoading,
    startDate: gameStartDate,
    endDate: gameEndDate,
    setStartDate: setGameStartDate,
    setEndDate: setGameEndDate,
    handleSearch: handleGameSearch
  } = usePatientDashboardLogic();

  // 기록 관련 로직
  const {
    dashboardData: recordDashboardData,
    loading: recordLoading,
    startDate: recordStartDate,
    endDate: recordEndDate,
    setStartDate: setRecordStartDate,
    setEndDate: setRecordEndDate,
    handleSearch: handleRecordSearch
  } = usePatientRecordLogic();

  const gameChartData = useChartDataLogic(gameDashboardData);
  const recordChartData = useRecordChartDataLogic(recordDashboardData);
  const { handlePrintToPDF } = usePDFGenerator();

  const { stats: gameStats, gameList, searchDate: gameSearchDate } = gameDashboardData || {};
  const { stats: recordStats, record, searchDate: recordSearchDate } = recordDashboardData || {};

  return (
      <div className="app-container d-flex flex-column">
        <FamilyHeader />
        <main className="content-area guardian-con">

          <ul className="menu-tab-con nav nav-tabs mb-2">
            <li className="nav-item">
              <a className={`nav-link ${activeTab === 'game' ? 'active' : ''}`} href="#" onClick={() => setActiveTab('game')}>게임</a>
            </li>
            <li className="nav-item">
              <a className={`nav-link ${activeTab === 'record'  ? 'active' : ''}`} href="#" onClick={() => setActiveTab('record')}>기록</a>
            </li>
          </ul>

          <div className="detail-title">
            <div><span>환자 01</span> 최근 활동</div>
            <div>
              <div className="icon-btn print-btn" onClick={handlePrintToPDF}></div>
            </div>
          </div>

          {activeTab === 'game' ? (
              <>
                {/* 게임 탭 내용 */}
                <GamePlayerStatItem stats={gameStats} loading={gameLoading.stats} />
                <GamePlayerDatePickerItem
                    startDate={gameStartDate}
                    endDate={gameEndDate}
                    setStartDate={setGameStartDate}
                    setEndDate={setGameEndDate}
                    handleSearch={handleGameSearch}
                />
                <GamePlayerChartAndGameItem
                    chartData={gameChartData}
                    loading={gameLoading}
                    searchDate={gameSearchDate}
                    gameList={gameList}
                />
              </>
          ) : (
              <>
                {/* 기록 탭 내용 */}
                <RecordStatItem stats={recordStats} loading={recordLoading.stats} />
                <GamePlayerDatePickerItem
                    startDate={recordStartDate}
                    endDate={recordEndDate}
                    setStartDate={setRecordStartDate}
                    setEndDate={setRecordEndDate}
                    handleSearch={handleRecordSearch}
                />
                <RecordChartAndDataItem
                    chartData={recordChartData}
                    loading={recordLoading}
                    searchDate={recordSearchDate}
                    record={record}
                />
              </>
          )}
        </main>

        <AlarmModal />
        <FamilyFooter />
      </div>
  );
}

export default PatientDetailPage;