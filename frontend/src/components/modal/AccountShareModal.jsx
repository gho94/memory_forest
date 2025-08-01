import React from 'react';
import '@/assets/css/family.css';

function AccountShareModal({ onClose }) {
  return (
    <div className="alarm-modal-overlay" onClick={onClose}>
      <div className="position-relative custom-modal" onClick={(e) => e.stopPropagation()}>
        <button className="custom-close" onClick={onClose}>&times;</button>
        <div className="text-center mb-3">
          <div className="center-group">
            <div className="logo" aria-label="기억 숲 로고"></div>
            <div className="title">계정 공유</div>
          </div>
        </div>

        <div className="modal-body-scroll d-flex flex-column gap-3">
          <div className="form-group">
            <label htmlFor="email">이메일 주소</label>
            <input type="email" className="form-control" id="email" placeholder="example@email.com" />
          </div>
          <button className="btn btn-primary w-100 mt-3">공유 요청 보내기</button>
        </div>
      </div>
    </div>
  );
}

export default AccountShareModal;
