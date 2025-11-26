import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { createAuthenticatedFetch } from '../utils/api';

// 사용자 타입 정의
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'user' | 'viewer';
}

// 인증 컨텍스트 타입 정의
interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<{ success: boolean; message: string }>;
  logout: () => void;
  verifyToken: () => Promise<boolean>;
}

// 컨텍스트 생성
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 인증 프로바이더 컴포넌트
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 컴포넌트 마운트 시 로컬 스토리지에서 토큰 확인
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const savedToken = localStorage.getItem('authToken');
        if (savedToken) {
          setToken(savedToken);
          const isValid = await verifyTokenWithServer(savedToken);
          if (!isValid) {
            // 토큰이 유효하지 않으면 제거
            localStorage.removeItem('authToken');
            setToken(null);
          }
        }
      } catch (error) {
        console.error('인증 초기화 오류:', error);
        localStorage.removeItem('authToken');
        setToken(null);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // 서버에서 토큰 검증
  const verifyTokenWithServer = async (tokenToVerify: string): Promise<boolean> => {
    try {
      const response = await fetch('/api/auth/verify', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${tokenToVerify}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.user) {
          setUser(data.user);
          return true;
        }
      }
      return false;
    } catch (error) {
      console.error('토큰 검증 오류:', error);
      return false;
    }
  };

  // 로그인 함수
  const login = async (username: string, password: string): Promise<{ success: boolean; message: string }> => {
    try {
      setIsLoading(true);
      
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (data.success && data.token) {
        // 로그인 성공
        setToken(data.token);
        setUser(data.user);
        localStorage.setItem('authToken', data.token);
        
        console.log('✅ 로그인 성공:', data.user.username);
        return { success: true, message: data.message };
      } else {
        // 로그인 실패
        return { success: false, message: data.message || '로그인에 실패했습니다.' };
      }
    } catch (error) {
      console.error('로그인 오류:', error);
      return { success: false, message: '서버 연결 오류가 발생했습니다.' };
    } finally {
      setIsLoading(false);
    }
  };

  // 로그아웃 함수
  const logout = async () => {
    try {
      // 서버에 로그아웃 요청 (선택사항)
      if (token) {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
      }
    } catch (error) {
      console.error('로그아웃 API 오류:', error);
    } finally {
      // 클라이언트 상태 정리
      setUser(null);
      setToken(null);
      localStorage.removeItem('authToken');
      console.log('✅ 로그아웃 완료');
    }
  };

  // 토큰 검증 함수
  const verifyToken = async (): Promise<boolean> => {
    if (!token) return false;
    return await verifyTokenWithServer(token);
  };

  // 인증 상태 계산
  const isAuthenticated = !!(user && token);

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    logout,
    verifyToken
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// 인증 컨텍스트 사용 훅
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth는 AuthProvider 내부에서 사용되어야 합니다.');
  }
  return context;
};

// 인증된 API 요청을 위한 헬퍼 함수 (utils/api.ts 사용)
export const useAuthenticatedFetch = () => {
  const { user, token } = useAuth();
  
  // createAuthenticatedFetch를 사용하여 인증된 fetch 함수 생성
  // 이제 모든 요청에 X-User-ID 헤더가 자동으로 포함됩니다
  return createAuthenticatedFetch(user, token);
};
