import React from 'react';
import '@/assets/css/family.css';

function GameAddModal({ onClose }) {
  return (
    <div className="alarm-modal-overlay" onClick={onClose}>
      <div className="position-relative custom-modal" onClick={(e) => e.stopPropagation()}>
        <button className="custom-close" onClick={onClose}>&times;</button>
        <div className="text-center mb-3">
          <div className="center-group">
            <div className="logo" aria-label="기억 숲 로고"></div>
            <div className="title">게임 추가</div>
          </div>
        </div>

        <div className="modal-body-scroll d-flex flex-column gap-3">
          <div className="form-group">
            <label htmlFor="game-title">게임 제목</label>
            <input type="text" className="form-control" id="game-title" placeholder="예: 회상 게임" />
          </div>
          <div className="form-group">
            <label htmlFor="game-desc">설명</label>
            <textarea className="form-control" id="game-desc" placeholder="게임 설명을 입력하세요" rows="3"></textarea>
          </div>
          <button className="btn btn-primary w-100 mt-3">게임 추가</button>
        </div>
      </div>
    </div>
  );
}

export default GameAddModal;
