import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// 전역 API URL 설정, 배포할 때 수정해야 함.
window.API_BASE_URL = 'http://localhost:8080';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);