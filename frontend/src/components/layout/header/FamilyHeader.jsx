import React from 'react';

const FamilyHeader = () => {
  return (
    <header className="app-header guardian-header">
      <div className="header-content">
        <div className="logo" role="img" aria-label="기억 숲 아이콘"></div>
        <div>
          <div className="app-header-text-top">기억</div>
          <div className="app-header-text-bottom">숲</div>
        </div>
      </div>
      <label htmlFor="toggle-alarm-modal" className="alarm"></label>
    </header>
  );
};

export default FamilyHeader;
