import React, { useState, useEffect } from 'react';
import html2pdf from 'html2pdf.js';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';

import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';
import WeeklyAccuracyChart from '@/components/charts/WeeklyAccuracyChart';
import GamePlayerDetailItem from '@/components/game/GamePlayerDetailItem';
import AlarmModal from '@/components/modal/AlarmModal';

// 간단한 스켈레톤 컴포넌트들
const StatSkeleton = () => (
    <div style={{
      background: '#f0f0f0',
      borderRadius: '4px',
      height: '15px',
      width: '40px',
      display: 'inline-block',
      opacity: 0.7
    }}></div>
);

const ChartSkeleton = () => (
    <div style={{
      borderRadius: '8px',
      height: '300px',
      width: '100%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: '#999',
      fontSize: '14px'
    }}>
      차트 로딩 중...
    </div>
);

const GameItemSkeleton = () => (
    <div className="game-item" style={{marginBottom: '15px'}}>
      <div style={{
        background: '#f0f0f0',
        borderRadius: '4px',
        height: '16px',
        width: '200px',
        marginBottom: '10px'
      }}></div>
      <div style={{
        background: '#f0f0f0',
        borderRadius: '4px',
        height: '14px',
        width: '100%',
        marginBottom: '15px'
      }}></div>
      <div style={{display: 'flex', gap: '10px'}}>
        {[...Array(4)].map((_, i) => (
            <div key={i} style={{
              background: '#f0f0f0',
              borderRadius: '4px',
              height: '40px',
              width: '80px'
            }}></div>
        ))}
      </div>
    </div>
);

//leb. user 완성되면 하드코딩한 user name 바꿔줘야 함.
function PatientDetailPage() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState({
    stats: true,
    chart: true,
    games: true
  });
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const userId = 'U0002'; // Mock - 원래는 searchParams.get('userId') || 'U0002';
  const gameId = null; // Mock - 원래는 searchParams.get('gameId');

  const parseSearchDate = (searchDateStr) => {
    if (!searchDateStr) return null;

    // "2025년 08월 08일" → "2025-08-08"
    const match = searchDateStr.match(/(\d{4})년 (\d{2})월 (\d{2})일/);
    if (match) {
      const [, year, month, day] = match;
      return `${year}-${month}-${day}`;
    }
    return null;
  };

  const fetchDashboardData = async (params = {}) => {
    try {
      // 로딩 상태를 세분화해서 관리
      setLoading({ stats: true, chart: true, games: true });

      const queryParams = new URLSearchParams({
        userId,
        ...(gameId && { gameId }),
        ...(params.startDate && { startDate: params.startDate }),
        ...(params.endDate && { endDate: params.endDate })
      });

      const response = await fetch(`${window.API_BASE_URL}/companion/game/dashboard?${queryParams}`);
      const data = await response.json();
      setDashboardData(data);

      // 단계적으로 로딩 해제 (자연스러운 UX를 위해)
      setTimeout(() => {
        setLoading(prev => ({ ...prev, stats: false }));
      }, 200);

      setTimeout(() => {
        setLoading(prev => ({ ...prev, chart: false }));
      }, 500);

      setTimeout(() => {
        setLoading(prev => ({ ...prev, games: false }));
      }, 800);

      if (data.searchDate) {
        const endDateStr = parseSearchDate(data.searchDate);
        if (endDateStr) {
          const endDateObj = new Date(endDateStr);
          const startDateObj = new Date(endDateObj);
          startDateObj.setDate(endDateObj.getDate() - 6);

          setEndDate(endDateStr);
          setStartDate(startDateObj.toISOString().split('T')[0]);
        }
      }
    } catch (error) {
      console.error('Dashboard API 호출 실패:', error);
      // 에러가 나도 로딩 상태는 해제
      setLoading({ stats: false, chart: false, games: false });
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [userId, gameId]);

  useEffect(() => {
    if (endDate) {
      const endDateObj = new Date(endDate);
      const startDateObj = new Date(endDateObj);
      startDateObj.setDate(endDateObj.getDate() - 6);

      const startDateStr = startDateObj.toISOString().split('T')[0];
      setStartDate(startDateStr);
    }
  }, [endDate]);

  // 검색 버튼 클릭 핸들러
  const handleSearch = () => {
    if (startDate && endDate) {
      fetchDashboardData({
        startDate: startDate,
        endDate: endDate
      });
    } else {
      alert('시작 날짜와 종료 날짜를 모두 선택해주세요.');
    }
  };

  const generateChartData = () => {
    if (!dashboardData || !dashboardData.weeklyChart || !dashboardData.searchDate) {
      return { categories: [], data: [] };
    }

    // 한국 시간대 기준으로 오늘 날짜 생성
    const searchDateStr = parseSearchDate(dashboardData.searchDate); // "2025-08-08"
    const baseDate = new Date(searchDateStr);
    baseDate.setHours(0, 0, 0, 0);

    const dates = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date(baseDate);
      date.setDate(baseDate.getDate() - i);
      dates.push(date);
    }

    // 날짜별 정답률 매핑 (문자열 키 사용)
    const chartDataMap = {};
    dashboardData.weeklyChart.forEach(item => {
      // API에서 온 날짜 그대로 사용
      chartDataMap[item.date] = parseFloat(item.accuracy || 0);
    });

    // 카테고리와 데이터 생성
    const categories = [];
    const data = [];

    dates.forEach(date => {
      // 카테고리 생성
      const dayNames = ['일', '월', '화', '수', '목', '금', '토'];
      const dayOfWeek = dayNames[date.getDay()];
      const category = `${date.getFullYear().toString().slice(2)}.${(date.getMonth() + 1).toString().padStart(2, '0')}.${date.getDate().toString().padStart(2, '0')}(${dayOfWeek})`;
      categories.push(category);

      // 데이터 매핑
      const dateStr = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
      const accuracy = chartDataMap[dateStr] || 0;
      data.push(accuracy);
    });

    return { categories, data };
  };

  const handlePrintToPDF = () => {
    const element = document.querySelector('.content-area.guardian-con');
    const printContent = element.innerHTML;

    // 새 창 열기
    const printWindow = window.open('', '_blank');

    // 새 창에 HTML 작성
    printWindow.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>활동 리포트</title>
      <style>
        /* 통계 영역 스타일링 */
        .patient-activity-con { 
          display: grid; 
          grid-template-columns: 1fr 1fr; 
          gap: 20px; 
          margin: 30px 0; 
          font-size: 16px;
          font-weight: 500;
        }
        
        .patient-activity-con .col-6 {
          background: #f8f9fa;
          padding: 15px;
          border-radius: 8px;
          border-left: 4px solid #007bff;
        }
        
        .patient-activity-con .col-6 span {
          font-weight: bold;
          color: #007bff;
          font-size: 18px;
        }
        
        /* 차트 영역 크게 만들기 */
        .chart { 
          margin: 30px 0;
          min-height: 450px !important; /* 차트 높이 강제 증가 */
        }
        
        .chart #chart {
          min-height: 450px !important;
        }
        
        .chart svg {
          min-height: 450px !important;
          width: 100% !important;
        }
        
        /* 게임 결과 아이템 */
        .game-item { 
          border: 1px solid #ddd; 
          padding: 15px; 
          margin: 15px 0; 
          border-radius: 8px; 
          background: #fff;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .option-btn {
          display: inline-block;
          padding: 10px 15px;
          margin: 5px;
          border: 1px solid #ccc;
          border-radius: 6px;
          background: #f9f9f9;
          font-weight: 500;
        }
        
        .correct-selected { 
          background: #d4edda; 
          border-color: #28a745;
          color: #155724;
        }
        
        .wrong-selected { 
          background: #f8d7da; 
          border-color: #dc3545;
          color: #721c24;
        }
        
        .correct-answer { 
          background: #d1ecf1; 
          border-color: #17a2b8;
          color: #0c5460;
        }
        
        /* 제목 스타일링 */
        .detail-title {
          font-size: 24px;
          font-weight: bold;
          margin-bottom: 30px;
          padding-bottom: 15px;
          border-bottom: 2px solid #007bff;
        }
        
        .game-date {
          font-size: 18px;
          font-weight: bold;
          color: #333;
          margin-bottom: 20px;
        }
        
        /* 차트 툴바 숨기기 */
        .apexcharts-toolbar { 
          display: none !important; 
        }
        
        @media print {
          .icon-btn, .search-btn, .date-picker-wrapper { 
            display: none !important; 
          }
          .apexcharts-toolbar { 
            display: none !important; 
          }
          
          /* 프린트할 때 차트 크기 유지 */
          .chart, .chart #chart, .chart svg {
            min-height: 400px !important;
          }
        }
      </style>
    </head>
    <body>
      ${printContent}
      <script>
        window.onload = function() {
          // 차트 크기 강제 조정
          setTimeout(() => {
            const chartElements = document.querySelectorAll('.chart svg');
            chartElements.forEach(chart => {
              chart.setAttribute('height', '450');
            });
            
            window.print();
            window.onafterprint = function() {
              window.close();
            }
          }, 1000); // 1초 후 프린트 (차트 로딩 대기)
        }
      </script>
    </body>
    </html>
  `);

    printWindow.document.close();
  };

  const { stats, gameList, searchDate } = dashboardData || {};
  const chartData = generateChartData();

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

          {/* 통계 영역 - 스켈레톤 또는 실제 데이터 */}
          <div className="patient-activity-con row">
            <div className="col-6">
              오늘 : {loading.stats ? <StatSkeleton /> : <><span>{stats?.todayScore}</span>점 (<span>{stats?.todayAccuracy}</span>%)</>}
            </div>
            <div className="col-6">
              이번주 참여율 : {loading.stats ? <StatSkeleton /> : <><span>{stats?.weeklyParticipation}</span>%</>}
            </div>
            <div className="col-6">
              어제 : {loading.stats ? <StatSkeleton /> : <><span>{stats?.yesterdayScore}</span>점 (<span>{stats?.yesterdayAccuracy}</span>%)</>}
            </div>
            <div className="col-6">
              전체 정답률 : {loading.stats ? <StatSkeleton /> : <><span>{stats?.overallAccuracy}</span>%</>}
            </div>
            <div className="col-6">
              일주일 정답률 : {loading.stats ? <StatSkeleton /> : <><span>{stats?.weeklyAccuracy}</span>%</>}
            </div>
            <div className="col-6">
              주간 정답률 : {loading.stats ? <StatSkeleton /> : <><span>{stats?.weeklyAccuracyDiff > 0 ? '+' : ''}{stats?.weeklyAccuracyDiff}</span>%</>}
            </div>
          </div>

          {/* 날짜 선택기 - 항상 표시 */}
          <div className="date-picker-wrapper">
            <label className="date-input readonly">
              <input
                  type="date"
                  name="startDate"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
              />
            </label>
            <span className="range-symbol">~</span>
            <label className="date-input">
              <input
                  type="date"
                  name="endDate"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
              />
            </label>
            <div className="search-btn" onClick={handleSearch}></div>
          </div>

          {/* 차트 및 게임 결과 */}
          <div className="chart-con">
            <div className="chart">
              {loading.chart ? (
                  <ChartSkeleton />
              ) : (
                  <WeeklyAccuracyChart
                      chartData={chartData.data}
                      categories={chartData.categories}
                  />
              )}
            </div>
            <div className="game-result">
              <div className="game-date">{searchDate || ''}</div>
              {loading.games ? (
                  // 게임 로딩 중일 때 스켈레톤
                  <>
                    <GameItemSkeleton />
                    <GameItemSkeleton />
                    <GameItemSkeleton />
                  </>
              ) : gameList?.length > 0 ? (
                  // 실제 게임 데이터
                  gameList.map((game, index) => (
                      <GamePlayerDetailItem key={`${game.gameId}-${game.gameSeq}`} game={game} />
                  ))
              ) : (
                  // 게임이 없을 때
                  <div className="no-game-message">진행된 게임이 존재하지 않습니다.</div>
              )}
            </div>
          </div>
        </main>
        <AlarmModal />
        <FamilyFooter />
      </div>
  );
}

export default PatientDetailPage;