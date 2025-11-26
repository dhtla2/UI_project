# 🔧 422 에러 해결 가이드

## 📋 422 에러란?

**422 Unprocessable Entity**: 서버가 요청을 이해했지만, 데이터가 유효성 검증에 실패했을 때 발생

---

## 🔍 원인 분석

### 백엔드에서 기대하는 필드 (PageVisitRequest)

```python
class PageVisitRequest(BaseModel):
    user_id: str              # 필수
    page_name: str            # 필수
    page_url: str             # 필수
    login_status: str = "visit"  # 기본값 있음
    visit_duration: Optional[int] = None
    session_id: Optional[str] = None
    referrer: Optional[str] = None
```

### 프론트엔드에서 보내는 데이터 (App.tsx)

```typescript
{
  user_id: userId,
  page_name: pageName,
  page_url: window.location.href,
  login_status: userId !== 'anonymous' ? 'logged_in' : 'guest',
  visit_duration: 0,
  session_id: sessionStorage.getItem('sessionId') || generateSessionId(),
  referrer: document.referrer || 'direct'
}
```

---

## 🐛 가능한 원인

### 1. **sessionId가 null일 수 있음**

`sessionStorage.getItem('sessionId')`가 null을 반환하면 `generateSessionId()`가 호출되지만, 타이밍 문제가 있을 수 있습니다.

### 2. **referrer가 빈 문자열일 수 있음**

`document.referrer`가 빈 문자열이면 문제가 될 수 있습니다.

### 3. **login_status 값이 예상과 다를 수 있음**

---

## ✅ 해결 방법

### 방법 1: App.tsx 수정 (권장)

**파일**: `dashboard/src/App.tsx`

```typescript
// 페이지 방문 로그 기록 함수
const logPageVisit = async (pageName: string, userId: string = 'anonymous') => {
  try {
    // 세션 ID 확보
    let sessionId = sessionStorage.getItem('sessionId');
    if (!sessionId) {
      sessionId = generateSessionId();
    }
    
    // 데이터 준비 (명확하게)
    const logData = {
      user_id: userId || 'anonymous',  // fallback 추가
      page_name: pageName || 'unknown',  // fallback 추가
      page_url: window.location.href || 'http://localhost',  // fallback 추가
      login_status: userId !== 'anonymous' ? 'logged_in' : 'guest',
      visit_duration: 0,
      session_id: sessionId,
      referrer: document.referrer || null  // null로 명시
    };
    
    console.log('[LOG] Sending page visit log:', logData);  // 디버깅용
    
    const response = await fetch('/ui/log/page-visit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(logData)
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('[LOG] Error response:', errorText);
    } else {
      console.log('[LOG] Page visit logged successfully');
    }
  } catch (error) {
    console.error('페이지 방문 로그 기록 실패:', error);
  }
};
```

### 방법 2: 백엔드에서 더 관대하게 받기

**파일**: `backend/models/schemas.py`

```python
from typing import Optional

class PageVisitRequest(BaseModel):
    user_id: str
    page_name: str
    page_url: str
    login_status: str = "visit"
    visit_duration: Optional[int] = 0  # 기본값 추가
    session_id: Optional[str] = None
    referrer: Optional[str] = None
    
    class Config:
        # 추가 필드 무시
        extra = "ignore"
```

---

## 🔍 디버깅 방법

### 1. 브라우저 개발자 도구에서 확인

**F12 → Network 탭**

1. 페이지를 이동하거나 새로고침
2. `/ui/log/page-visit` 요청 찾기
3. **Request** 탭에서 실제 전송된 데이터 확인:

```json
// 👇 이런 형태여야 함
{
  "user_id": "admin",
  "page_name": "AIS",
  "page_url": "http://localhost:3000/",
  "login_status": "logged_in",
  "visit_duration": 0,
  "session_id": "session_1234567890_abc123",
  "referrer": null
}
```

4. **Response** 탭에서 에러 메시지 확인:

```json
// 422 에러 시 상세 내용
{
  "detail": [
    {
      "loc": ["body", "session_id"],  // 문제가 있는 필드
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 2. 백엔드 로그 확인

```bash
cd /home/cotlab/UI_project_new/backend
python3 main_new.py

# 로그에서 다음과 같은 내용이 나타날 수 있음:
# ERROR: Validation error for PageVisitRequest
# body -> session_id: field required
```

### 3. 콘솔 로그 추가

**App.tsx에 디버깅 로그 추가**:

```typescript
useEffect(() => {
  const userId = user?.username || 'anonymous';
  console.log('=== Page Visit Log Debug ===');
  console.log('Current Page:', currentPage);
  console.log('User:', user);
  console.log('User ID:', userId);
  console.log('Session ID:', sessionStorage.getItem('sessionId'));
  console.log('==========================');
  
  logPageVisit(currentPage, userId);
}, [currentPage, user]);
```

---

## 🚀 빠른 수정

### 1단계: App.tsx 전체 교체

**파일**: `dashboard/src/App.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import './App.css';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './components/auth/LoginPage';
import LoadingSpinner from './components/common/LoadingSpinner';
import AISPage from './components/AISPage';
import TOSPage from './components/TOSPage';
import TCPage from './components/TCPage';
import QCPage from './components/QCPage';
import QualityCheckPage from './components/QualityCheckPage';

// 세션 ID 생성 함수 (먼저 정의)
const generateSessionId = (): string => {
  const existingId = sessionStorage.getItem('sessionId');
  if (existingId) return existingId;
  
  const newId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  sessionStorage.setItem('sessionId', newId);
  return newId;
};

// 페이지 방문 로그 기록 함수 (개선됨)
const logPageVisit = async (pageName: string, userId: string = 'anonymous') => {
  try {
    const logData = {
      user_id: userId || 'anonymous',
      page_name: pageName || 'unknown',
      page_url: window.location.href || 'http://localhost:3000',
      login_status: userId !== 'anonymous' ? 'logged_in' : 'guest',
      visit_duration: 0,
      session_id: generateSessionId(),  // 항상 유효한 값 보장
      referrer: document.referrer || null
    };
    
    // 개발 환경에서 로그 출력
    if (process.env.NODE_ENV === 'development') {
      console.log('[Page Visit]', logData);
    }
    
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
    console.error('[Page Visit Failed]', error);
  }
};

// 나머지 코드는 동일...
```

### 2단계: 브라우저 캐시 삭제

```
1. F12 (개발자 도구)
2. Application 탭
3. Storage → Clear site data
4. 페이지 새로고침 (Ctrl+Shift+R)
```

### 3단계: 테스트

```bash
# 백엔드 재시작
cd /home/cotlab/UI_project_new/backend
pkill -f "python.*main_new.py"
python3 main_new.py

# 프론트엔드 재시작
cd /home/cotlab/UI_project_new/dashboard
npm start
```

---

## 📊 예상 결과

### 성공 시 (200 OK)

**브라우저 콘솔**:
```
[Page Visit] {user_id: "admin", page_name: "AIS", ...}
```

**백엔드 로그**:
```
INFO: POST /ui/log/page-visit - 200 OK
```

**DB 확인**:
```bash
python3 verify_page_visits.py

# 결과:
user_id     | 방문 횟수
------------|----------
admin       | 1회   ✅ 새로운!
```

### 실패 시 (422)

**브라우저 콘솔**:
```
[Page Visit Error] 422 {"detail":[{"loc":["body","session_id"],"msg":"field required"}]}
```

→ 위의 수정 방법 적용

---

## 💡 추가 팁

### 일시적 해결 (테스트용)

백엔드에서 모든 필드를 Optional로:

```python
class PageVisitRequest(BaseModel):
    user_id: Optional[str] = "anonymous"
    page_name: Optional[str] = "unknown"
    page_url: Optional[str] = "/"
    login_status: Optional[str] = "visit"
    visit_duration: Optional[int] = 0
    session_id: Optional[str] = None
    referrer: Optional[str] = None
```

---

## 🎯 체크리스트

- [ ] App.tsx의 `logPageVisit` 함수 업데이트
- [ ] `generateSessionId` 함수가 올바르게 호출되는지 확인
- [ ] 브라우저 개발자 도구에서 실제 요청 데이터 확인
- [ ] 백엔드 로그에서 에러 메시지 확인
- [ ] 브라우저 캐시 삭제
- [ ] 서버 재시작
- [ ] 테스트

---

## 🆘 여전히 안 되면?

**1. 에러 메시지 전체 복사**:
```
F12 → Network → /ui/log/page-visit → Response 탭
```

**2. 전송된 데이터 확인**:
```
F12 → Network → /ui/log/page-visit → Payload 탭
```

**3. 백엔드 로그 확인**:
```bash
cd backend
tail -50 logs/*.log
```

이 정보를 가지고 다시 확인하면 정확한 원인을 찾을 수 있습니다!

