/**
 * Authenticated Fetch Wrapper
 * 
 * 모든 HTTP 요청에 자동으로 인증 정보와 사용자 ID를 포함시킵니다.
 * 로그인한 사용자 ID가 백엔드 로깅 시스템에 자동으로 전달됩니다.
 */

import { User } from '../contexts/AuthContext';

/**
 * 세션 ID 생성 함수
 * 브라우저 세션마다 고유한 ID를 생성합니다.
 */
export const generateSessionId = (): string => {
  // 기존 세션 ID 확인
  const existingSessionId = sessionStorage.getItem('sessionId');
  if (existingSessionId) {
    return existingSessionId;
  }
  
  // 새로운 세션 ID 생성
  const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  sessionStorage.setItem('sessionId', sessionId);
  return sessionId;
};

/**
 * 인증된 Fetch 함수 생성
 * 
 * @param user 현재 로그인한 사용자 정보
 * @param token 인증 토큰
 * @returns 인증 헤더가 포함된 fetch 함수
 */
export const createAuthenticatedFetch = (user: User | null, token: string | null) => {
  return async (url: string, options: RequestInit = {}) => {
    // 기본 헤더 설정
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      // 사용자 ID 헤더 (로그인 시 username, 비로그인 시 anonymous)
      'X-User-ID': user?.username || 'anonymous',
      // 세션 ID 헤더
      'X-Session-ID': generateSessionId(),
      // 추가 메타데이터
      'X-User-Role': user?.role || 'guest',
      'X-Request-Time': new Date().toISOString(),
    };
    
    // 인증 토큰이 있으면 Authorization 헤더 추가
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // 기존 헤더와 병합
    const mergedHeaders = {
      ...headers,
      ...(options.headers as Record<string, string>),
    };
    
    // 요청 정보 로깅 (개발 환경)
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Request] ${options.method || 'GET'} ${url}`);
      console.log(`[User] ${user?.username || 'anonymous'} (${user?.role || 'guest'})`);
    }
    
    try {
      // Fetch 실행
      const response = await fetch(url, {
        ...options,
        headers: mergedHeaders,
      });
      
      // 응답 로깅 (개발 환경)
      if (process.env.NODE_ENV === 'development') {
        console.log(`[API Response] ${response.status} ${response.statusText}`);
      }
      
      return response;
    } catch (error) {
      console.error(`[API Error] ${url}:`, error);
      throw error;
    }
  };
};

/**
 * React Hook: useAuthenticatedFetch
 * 
 * 컴포넌트에서 쉽게 사용할 수 있는 Hook
 * 
 * @example
 * ```typescript
 * import { useAuthenticatedFetch } from '../../utils/api';
 * 
 * const MyComponent = () => {
 *   const authenticatedFetch = useAuthenticatedFetch();
 *   
 *   const fetchData = async () => {
 *     const response = await authenticatedFetch('/api/data');
 *     const data = await response.json();
 *   };
 * };
 * ```
 */
export const useAuthenticatedFetch = () => {
  // AuthContext는 직접 import하지 않고 외부에서 전달받음
  // 이는 순환 참조를 방지하기 위함
  throw new Error(
    'useAuthenticatedFetch는 직접 사용할 수 없습니다. ' +
    'AuthContext에서 제공하는 useAuthenticatedFetch를 사용하세요.'
  );
};

/**
 * 페이지 방문 로그 전송 헬퍼 함수
 * 
 * @param authenticatedFetch 인증된 fetch 함수
 * @param pageName 페이지 이름
 * @param additionalData 추가 데이터
 */
export const logPageVisit = async (
  authenticatedFetch: (url: string, options?: RequestInit) => Promise<Response>,
  pageName: string,
  additionalData?: {
    userId?: string;
    loginStatus?: string;
    visitDuration?: number;
  }
) => {
  try {
    await authenticatedFetch('/ui/log/page-visit', {
      method: 'POST',
      body: JSON.stringify({
        page_name: pageName,
        page_url: window.location.href,
        referrer: document.referrer || 'direct',
        visit_duration: additionalData?.visitDuration || 0,
        ...additionalData,
      }),
    });
  } catch (error) {
    console.error('페이지 방문 로그 기록 실패:', error);
  }
};

/**
 * API 응답 타입 체크 헬퍼
 */
export const handleApiResponse = async <T = any>(response: Response): Promise<T> => {
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API Error ${response.status}: ${errorText}`);
  }
  
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return await response.json();
  }
  
  return await response.text() as any;
};

/**
 * 타임아웃을 가진 Fetch
 */
export const fetchWithTimeout = async (
  url: string,
  options: RequestInit = {},
  timeout: number = 30000
): Promise<Response> => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeout}ms`);
    }
    throw error;
  }
};

