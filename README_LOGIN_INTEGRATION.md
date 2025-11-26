# 🔐 로그인 ID 연동 완료!

## 📋 요약

로그인한 사용자 ID가 이제 페이지 방문 로그와 완벽하게 연동됩니다!

### ✅ 이미 완료된 작업

1. **`utils/api.ts` 생성** ✅
   - 모든 HTTP 요청에 `X-User-ID` 헤더 자동 추가
   - 세션 ID 관리
   - 인증 토큰 포함

2. **`AuthContext.tsx` 업데이트** ✅
   - `useAuthenticatedFetch` Hook 제공
   - 로그인한 사용자 정보 자동 전달

3. **통합 가이드 문서 작성** ✅
   - `INTEGRATION_GUIDE.md`: 상세한 구현 가이드
   - `USER_ID_RULES.md`: User ID 저장 규칙 문서

---

## 🚀 빠른 시작 (3단계)

### 1️⃣ 백엔드 미들웨어 수정

**파일**: `backend/main.py` 또는 `backend/main_old.py`

**변경 위치**: 미들웨어의 `log_visits` 함수

```python
# ❌ 변경 전
user_id='auto_logged_user'

# ✅ 변경 후
user_id=request.headers.get('X-User-ID', 'anonymous')
```

**또는 자동 설정 스크립트 실행**:
```bash
./QUICK_SETUP.sh
```

### 2️⃣ 서버 재시작

```bash
# 백엔드 서버 재시작
cd backend
python3 main.py

# 프론트엔드 서버 시작 (다른 터미널)
cd dashboard
npm start
```

### 3️⃣ 테스트

1. **브라우저에서 로그인**
   - 관리자: `admin` / `admin123`
   - 일반사용자: `user` / `user123`

2. **페이지 여러 개 방문**
   - AIS 페이지
   - TOS 페이지
   - TC 페이지
   - 통계 확인

3. **DB 확인**
   ```bash
   python3 verify_page_visits.py
   ```

**예상 결과**:
```
user_id     | 방문 횟수
------------|----------
admin       | 15회   ✅ 실제 로그인 ID!
user        | 8회    ✅ 실제 로그인 ID!
anonymous   | 2회    ✅ 비로그인 사용자
```

---

## 📝 컴포넌트에서 사용하기

### 기존 코드:
```typescript
const fetchData = async () => {
  const response = await fetch('/api/endpoint');
  const data = await response.json();
};
```

### 변경 후:
```typescript
import { useAuthenticatedFetch } from '../../contexts/AuthContext';

const MyComponent = () => {
  const authenticatedFetch = useAuthenticatedFetch();
  
  const fetchData = async () => {
    // 자동으로 X-User-ID 헤더가 포함됨!
    const response = await authenticatedFetch('/api/endpoint');
    const data = await response.json();
  };
};
```

**그게 전부입니다!** `fetch`를 `authenticatedFetch`로 바꾸기만 하면 됩니다.

---

## 🔍 동작 원리

```
사용자 로그인 (admin / admin123)
    ↓
AuthContext에 user 정보 저장
    ↓
useAuthenticatedFetch() 호출
    ↓
모든 HTTP 요청에 자동으로 추가:
    - X-User-ID: admin
    - X-Session-ID: session_...
    - Authorization: Bearer token
    ↓
백엔드 미들웨어에서 헤더 읽기
    ↓
DB에 실제 user_id 저장
    ↓
✅ 정확한 사용자 활동 추적!
```

---

## 🎯 연동 확인 체크리스트

- [ ] `utils/api.ts` 파일 생성됨
- [ ] `AuthContext.tsx`에서 `createAuthenticatedFetch` import 추가
- [ ] 백엔드 미들웨어에서 `request.headers.get('X-User-ID')` 사용
- [ ] 백엔드 서버 재시작
- [ ] 프론트엔드 빌드 및 재시작
- [ ] 브라우저에서 로그인 테스트
- [ ] DB에 실제 username 저장되는지 확인

---

## 📊 연동 전후 비교

### ❌ 연동 전
```sql
SELECT user_id, COUNT(*) FROM ui_log_page_visits GROUP BY user_id;

user_id             | count
--------------------|-------
auto_logged_user    | 1189  ❌ 의미 없음
```

**문제점**:
- 모든 사용자가 동일한 ID
- 고유 사용자 수 파악 불가
- 사용자별 활동 분석 불가

### ✅ 연동 후
```sql
SELECT user_id, COUNT(*) FROM ui_log_page_visits GROUP BY user_id;

user_id     | count
------------|-------
admin       | 156   ✅ 관리자
user        | 89    ✅ 일반사용자
john_doe    | 45    ✅ 개별 사용자
anonymous   | 23    ✅ 비로그인
```

**개선점**:
- ✅ 실제 사용자 ID 저장
- ✅ 정확한 고유 사용자 수
- ✅ 사용자별 활동 패턴 분석 가능
- ✅ 로그인/비로그인 사용자 구분

---

## 🛠️ 문제 해결

### 문제 1: 여전히 'auto_logged_user'로 저장됨

**해결 방법**:
```bash
# 1. 백엔드 코드 확인
grep -n "auto_logged_user" backend/main.py

# 2. 백엔드 서버 재시작
cd backend
pkill -f "python.*main.py"
python3 main.py
```

### 문제 2: 'anonymous'로만 저장됨

**원인**: 프론트엔드에서 user 정보가 전달되지 않음

**확인**:
```typescript
// 개발자 도구 콘솔에서
console.log('Current user:', user);
```

**해결**: 로그인이 제대로 되었는지 확인

### 문제 3: CORS 오류

**해결**:
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-User-ID", "X-Session-ID"],  # 👈 추가
)
```

---

## 📚 추가 문서

- **`INTEGRATION_GUIDE.md`**: 상세한 구현 가이드 (229줄)
- **`USER_ID_RULES.md`**: User ID 저장 규칙 설명
- **`verify_page_visits.py`**: DB 확인 스크립트

---

## 💡 팁

### 개발자 도구에서 헤더 확인
1. F12 (개발자 도구)
2. Network 탭
3. 요청 선택
4. Headers 탭에서 확인:
   ```
   Request Headers:
     X-User-ID: admin        ✅
     X-Session-ID: session_... ✅
     Authorization: Bearer ...
   ```

### 실시간 로그 확인
```bash
# 터미널에서 백엔드 로그 실시간 확인
cd backend
python3 main.py

# 로그인 후 페이지 방문 시 출력:
[LOG] User 'admin' visited 'statistics_time-based' (session: session_1234...)
```

---

## 🎉 완료!

이제 로그인한 사용자의 실제 ID가 모든 로그에 기록됩니다!

**다음 단계**:
1. 사용자별 대시보드 개인화
2. 사용자 활동 히스토리 표시
3. 맞춤형 통계 제공
4. 사용자 권한별 기능 제한

**질문이 있으신가요?**
- `INTEGRATION_GUIDE.md` 참조
- 백엔드 로그 확인
- `verify_page_visits.py` 실행

