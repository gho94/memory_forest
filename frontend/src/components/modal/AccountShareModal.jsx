import React from 'react';
import '@/assets/css/family.css';

function AccountShareModal({ onClose }) {
  return (
    <>
      {/* 계정 공유 모달 */}
      <input type="checkbox" id="toggle-account-modal" />
      <div className="modal-overlay account-modal-overlay">
        <div className="position-relative custom-modal">
          <label htmlFor="toggle-account-modal" className="custom-close" onClick={onClose}>
            &times;
          </label>
          <div className="text-center mb-3">
            <div className="center-group">
              <div className="logo" aria-label="기억 숲 로고"></div>
              <div className="title">계정 공유</div>
            </div>
          </div>
          <div className="modal-body-scroll d-flex flex-column gap-3">
            <div className="qr-code-con">
              <div className="qr-code">qr</div>
            </div>
            <div className="row gx-0 share-icon-con">
              <div className="col-6 me-4 kakaotalk-icon"></div>
              <div className="col-6 link-icon"></div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default AccountShareModal;
