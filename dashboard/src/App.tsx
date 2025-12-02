import React, { useState, useEffect } from 'react';
import './App.css';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './components/auth/LoginPage';
import LoadingSpinner from './components/common/LoadingSpinner';
import AISPage from './components/AISPage';
import TOSPage from './components/TOSPage';
import TCPage from './components/TCPage';
import QCPage from './components/QCPage';
import YTPage from './components/YTPage';
import PortMisVsslNoPage from './components/PortMisVsslNoPage';
import TosVsslNoPage from './components/TosVsslNoPage';
import VsslSpecInfoPage from './components/VsslSpecInfoPage';
import QualityCheckPage from './components/QualityCheckPage';

// 페이지 방문 로그 기록 함수
const logPageVisit = async (pageName: string, userId: string = 'anonymous') => {
  try {
    // 세션 ID 확보 (항상 유효한 값 보장)
    let sessionId = sessionStorage.getItem('sessionId');
    if (!sessionId) {
      sessionId = generateSessionId();
    }
    
    // 로그 데이터 준비
    const logData = {
      user_id: userId || 'anonymous',
      page_name: pageName || 'unknown',
      page_url: window.location.href || 'http://localhost:3000',
      login_status: userId !== 'anonymous' ? 'logged_in' : 'guest',
      visit_duration: 0,
      session_id: sessionId,
      referrer: document.referrer || ''  // 빈 문자열로 변경
    };
    
    console.log('[Page Visit Log]', logData);  // 디버깅용
    
    const response = await fetch('/ui/log/page-visit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(logData)
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('[Page Visit Error]', response.status, errorText);
    }
  } catch (error) {
    console.error('페이지 방문 로그 기록 실패:', error);
  }
};

// 세션 ID 생성 함수
const generateSessionId = () => {
  const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  sessionStorage.setItem('sessionId', sessionId);
  return sessionId;
};

// 대시보드 컴포넌트 (인증된 사용자용)
const Dashboard: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck'>('AIS');
  const { user } = useAuth();

  // 페이지 변경 시 로그 기록
  useEffect(() => {
    const userId = user?.username || 'anonymous';
    logPageVisit(currentPage, userId);
  }, [currentPage, user]);

  const handlePageChange = (page: 'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck') => {
    setCurrentPage(page);
  };

  return (
    <div className="App">
      {/* 현재 페이지 렌더링 */}
      {currentPage === 'AIS' ? (
        <AISPage 
          currentPage={currentPage}
          onPageChange={handlePageChange}
        />
      ) : currentPage === 'TOS' ? (
        <TOSPage 
          currentPage={currentPage}
          onPageChange={handlePageChange}
        />
      ) : currentPage === 'TC' ? (
        <TCPage 
          currentPage={currentPage}
          onPageChange={handlePageChange}
        />
      ) : currentPage === 'QC' ? (
        <QCPage 
          currentPage={currentPage}
          onPageChange={handlePageChange}
        />
      ) : currentPage === 'YT' ? (
        <YTPage 
          currentPage={currentPage}
          onPageChange={handlePageChange}
        />
      ) : currentPage === 'PortMisVsslNo' ? (
        <PortMisVsslNoPage 
          currentPage={currentPage}
          onPageChange={handlePageChange}
        />
      ) : currentPage === 'TosVsslNo' ? (
        <TosVsslNoPage 
          currentPage={currentPage}
          onPageChange={handlePageChange}
        />
      ) : currentPage === 'VsslSpecInfo' ? (
        <VsslSpecInfoPage 
          currentPage={currentPage}
          onPageChange={handlePageChange}
        />
      ) : (
        <QualityCheckPage 
          currentPage={currentPage}
          onPageChange={handlePageChange}
        />
      )}
    </div>
  );
};

// 메인 앱 컴포넌트 (인증 체크)
const AppContent: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  // 🔓 임시: 로그인 비활성화 - 나중에 활성화하려면 아래 주석을 해제하세요
  // // 로딩 중
  // if (isLoading) {
  //   return <LoadingSpinner message="인증 확인 중..." />;
  // }

  // // 인증되지 않은 경우 로그인 페이지
  // if (!isAuthenticated) {
  //   return <LoginPage />;
  // }

  // 인증 없이 대시보드 직접 표시
  return <Dashboard />;
};

// 루트 App 컴포넌트
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
