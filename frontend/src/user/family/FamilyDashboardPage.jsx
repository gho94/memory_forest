import React, { useState } from 'react';
import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';

import AlarmModal from '@/components/modal/AlarmModal';
import AccountShareModal from '@/components/modal/AccountShareModal';
import GameAddModal from '@/components/modal/GameAddModal';

import '@/assets/css/common.css';
import '@/assets/css/family.css';

function FamilyDashboardPage() {
  const [activeTab, setActiveTab] = useState('account');
  const [showAlarmModal, setShowAlarmModal] = useState(false);
  const [showAccountModal, setShowAccountModal] = useState(false);
  const [showGameModal, setShowGameModal] = useState(false);

  return (
    <div className="app-container d-flex flex-column">
      <FamilyHeader />

      {/* 모달 영역 */}
      {showAlarmModal && (
        <AlarmModal onClose={() => setShowAlarmModal(false)} />
      )}
      {showAccountModal && (
        <AccountShareModal onClose={() => setShowAccountModal(false)} />
      )}
      {showGameModal && (
        <GameAddModal onClose={() => setShowGameModal(false)} />
      )}

      <main className="content-area family-con">
        <div className="header-box">
          <div className="page-title">환자01 님</div>
          <button
            className="btn-alarm"
            onClick={() => setShowAlarmModal(true)}
          >
            <span className="blind">알림</span>
          </button>
        </div>

        <ul className="nav nav-tabs tab-lg mb-4">
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'account' ? 'active' : ''}`}
              onClick={() => setActiveTab('account')}
            >
              계정
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'game' ? 'active' : ''}`}
              onClick={() => setActiveTab('game')}
            >
              게임목록
            </button>
          </li>
        </ul>

        {/* 계정 탭 */}
        {activeTab === 'account' && (
          <div className="account-con">
            <div className="account-header">
              <div className="title">공유 계정</div>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setShowAccountModal(true)}
              >
                계정 공유
              </button>
            </div>

            <div className="row row-cols-2 row-cols-sm-3 row-cols-lg-4">
              {[1, 2, 3].map((_, idx) => (
                <div key={idx} className="col">
                  <div className="account-card">
                    <div className="profile-img"></div>
                    <div className="account-info">
                      <div className="user-name">가족이름</div>
                      <div className="email">test@email.com</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 게임 목록 탭 */}
        {activeTab === 'game' && (
          <div className="game-con">
            <div className="account-header">
              <div className="title">게임 목록</div>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setShowGameModal(true)}
              >
                게임 추가
              </button>
            </div>

            <div className="row row-cols-2 row-cols-sm-3 row-cols-lg-4">
              {[1, 2, 3].map((_, idx) => (
                <div key={idx} className="col">
                  <div className="game-card">
                    <div className="thumbnail"></div>
                    <div className="game-info">
                      <div className="title">회상 게임</div>
                      <div className="desc">단기 기억력을 향상시키는 게임</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      <FamilyFooter />
    </div>
  );
}

export default FamilyDashboardPage;
