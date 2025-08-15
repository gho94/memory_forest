import React from 'react';

function FamilyFooter() {
    // 현재 경로 가져오기
    const currentPath = window.location.pathname;

    // 각 메뉴 항목 정의
    const menuItems = [
        {
            href: '/companion/dashboard',
            icon: 'home',
            label: '홈',
            path: ['/companion/dashboard'] // 배열로 변경
        },
        {
            href: '/companion/profileadd',
            icon: 'patient',
            label: '기록자',
            path: ['/companion/profileadd', '/companion/detail'] // 여러 경로 지원
        },
        {
            href: '/companion/games/create',
            icon: 'game',
            label: '게임',
            path: ['/companion/games'],
            hasGameCon: true // game-con 클래스 적용용
        },
        {
            href: '/companion/mypage',
            icon: 'user',
            label: '내정보',
            path: ['/companion/mypage']
        }
    ];

    // 현재 경로와 메뉴 경로가 일치하는지 확인하는 함수
    const isActive = (menuPaths) => {
        // path가 배열인 경우 각 경로를 체크
        return menuPaths.some(menuPath =>
            currentPath === menuPath || currentPath.startsWith(menuPath + '/')
        );
    };

    return (
        <footer className="app-footer guardian">
            {menuItems.map((item, index) => (
                <a
                    key={index}
                    href={item.href}
                    className={`nav-item d-flex flex-column align-items-center text-decoration-none ${
                        isActive(item.path) ? 'active' : ''
                    } ${item.hasGameCon ? 'game-con' : ''}`}
                >
                    <span className={`icon ${item.icon}`}></span>
                    <span className="label">{item.label}</span>
                </a>
            ))}
        </footer>
    );
}

export default FamilyFooter;