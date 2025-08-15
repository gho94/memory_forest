import React from 'react';
import '@/assets/css/footer.css';

function PatientFooter() {
    // 현재 경로 가져오기
    const currentPath = window.location.pathname;

    // 각 메뉴 항목 정의
    const menuItems = [
        {
            href: '/recorder/dashboard',
            icon: 'home',
            label: '홈',
            path: '/recorder/dashboard'
        },
        {
            href: '/recorder/game',
            icon: 'game',
            label: '게임',
            path: '/recorder/game'
        },
        {
            href: '/recorder/record/list',
            icon: 'record',
            label: '기록',
            path: '/recorder/record'
        },
        {
            href: '/recorder/chart',
            icon: 'chart',
            label: '진행도',
            path: '/recorder/chart'
        },
        {
            href: '/recorder/mypage',
            icon: 'user',
            label: '내 정보',
            path: '/recorder/mypage'
        }
    ];

    const isActive = (menuPath) => {
        return currentPath === menuPath || currentPath.startsWith(menuPath + '/');
    };

    return (
        <footer className="app-footer">
            {menuItems.map((item, index) => (
                <a
                    key={index}
                    href={item.href}
                    className={`nav-item d-flex flex-column align-items-center text-decoration-none ${
                        isActive(item.path) ? 'active' : ''
                    } ${item.icon === 'game' || item.icon === 'record' || item.icon === 'home' ? 'game-con' : ''}`}
                >
                    <span className={`icon ${item.icon}`}></span>
                    <span className="label">{item.label}</span>
                </a>
            ))}
        </footer>
    );
}

export default PatientFooter;