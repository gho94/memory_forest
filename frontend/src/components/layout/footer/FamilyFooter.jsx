function FamilyFooter() {
    return (
        <footer className="app-footer guardian">
            <a
                href="#"
                className="nav-item active d-flex flex-column align-items-center text-decoration-none"
            >
                <span className="icon home"></span>
                <span className="label">홈</span>
            </a>
            <a
                href="#"
                className="nav-item d-flex flex-column align-items-center text-decoration-none"
            >
                <span className="icon patient"></span>
                <span className="label">기록자</span>
            </a>
            <a
                href="#"
                className="nav-item d-flex game-con flex-column align-items-center text-decoration-none"
            >
                <span className="icon game"></span>
                <span className="label">게임</span>
            </a>
            <a
                href="#"
                className="nav-item d-flex flex-column align-items-center text-decoration-none"
            >
                <span className="icon user"></span>
                <span className="label">내정보</span>
            </a>
        </footer>
    );
}

export default FamilyFooter;
