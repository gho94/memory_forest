import '../../../assets/css/common/header.css';

function PatientHeader() {
  return (
    <header className="app-header">
      <div className="logo" role="img" aria-label="기억 숲 아이콘"></div>
      <div>
        <div className="app-header-text-top">기억</div>
        <div className="app-header-text-bottom">숲</div>
      </div>
    </header>
  );
}

export default PatientHeader;
