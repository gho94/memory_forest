function AlarmModal() {
    return (
        <>
            {/* 모달을 열기 위한 체크박스 */}
            <input type="checkbox" id="toggle-alarm-modal" className="toggle-checkbox"/>

            {/* 모달 오버레이 */}
            <div className="modal-overlay alarm-modal-overlay">
                <div className="position-relative custom-modal">
                    <label htmlFor="toggle-alarm-modal" className="custom-close">&times;</label>
                    <div className="text-center mb-3">
                        <div className="center-group">
                            <div className="logo" aria-label="기억 숲 로고"></div>
                            <div className="title">알림</div>
                        </div>
                    </div>
                    <div className="modal-body-scroll d-flex flex-column gap-3">
                        {[true, false].map((active, idx) => (
                            <div key={idx}
                                 className={`alert-card ${active ? 'active' : 'inactive'} d-flex align-items-start gap-2`}>
                                <div className="profile-img" alt="avatar"/>
                                <div>
                                    <div className="patient-con">
                                        <span className="patient-name">환자01</span>
                                        <span className="patient-reg-date">2025.06.20 15:20</span>
                                    </div>
                                    <div className="alarm-content">
                                        오늘의 게임을 완료하였습니다.<br/>
                                        지금 바로 결과를 확인해보세요.
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </>
    );
}

export default AlarmModal;
