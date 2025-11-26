# 의존성 분석 및 리팩토링 계획

## 📦 **현재 의존성**

### **외부 라이브러리**
- `fastapi` - 웹 프레임워크
- `uvicorn` - ASGI 서버
- `pydantic` - 데이터 검증 및 모델
- `pandas` - 데이터 처리
- `numpy` - 수치 계산
- `pymysql` - MySQL 데이터베이스 연결

### **내부 모듈**
- `ais_service.py` - AIS 데이터 서비스
- `ui_data_service.py` - UI 데이터 서비스

### **Pydantic 모델들 (중복 발견!)**
```python
# 중복된 모델들
class PageVisitRequest(BaseModel):  # 라인 288과 562에 중복 정의
class UIStatisticsResponse(BaseModel):  # 라인 297과 571에 중복 정의

# 기타 모델들
class QualityCheckRequest(BaseModel)
class QualityCheckResult(BaseModel)
class QualityCheckHistory(BaseModel)
class AISInfoResponse(BaseModel)
class StatisticsResponse(BaseModel)
```

## 🎯 **리팩토링 우선순위**

### **1순위: 중복 제거**
- 중복된 Pydantic 모델 통합
- 중복된 함수 로직 통합

### **2순위: 모델 분리**
- 모든 Pydantic 모델을 `models/schemas.py`로 이동
- 도메인별 모델 그룹화

### **3순위: 서비스 레이어 구축**
- 데이터베이스 로직을 서비스로 분리
- 비즈니스 로직과 API 로직 분리

### **4순위: 라우터 분리**
- 기능별 라우터 파일 생성
- 엔드포인트 분산

## 🏗️ **마이그레이션 전략**

### **Phase 1: 기반 구조 구축**
1. `config/` 설정 파일 생성
2. `models/schemas.py` 모델 통합
3. `services/database.py` 공통 DB 로직

### **Phase 2: 서비스 레이어 구축**
1. `services/ais_service.py` 개선
2. `services/tos_service.py` 생성
3. `services/tc_service.py` 생성
4. `services/qc_service.py` 생성
5. `services/ui_service.py` 생성

### **Phase 3: 라우터 분리**
1. `routers/ais_routes.py` 구현
2. `routers/tos_routes.py` 구현
3. `routers/tc_routes.py` 구현
4. `routers/qc_routes.py` 구현
5. `routers/dashboard_routes.py` 구현
6. `routers/ui_routes.py` 구현

### **Phase 4: 테스트 및 검증**
1. 각 모듈별 단위 테스트
2. API 호환성 테스트
3. 성능 비교 테스트

## 🔧 **기술적 고려사항**

### **데이터베이스 연결**
- 현재: 각 함수에서 개별 연결 생성
- 개선: 연결 풀 사용, 의존성 주입 패턴

### **에러 처리**
- 현재: 개별 try-catch 블록
- 개선: 중앙화된 예외 처리

### **로깅**
- 현재: print 문 사용
- 개선: 구조화된 로깅 시스템

### **설정 관리**
- 현재: 하드코딩된 설정값
- 개선: 환경변수 기반 설정

## 📊 **예상 효과**

### **코드 품질**
- 4008줄 → 각 파일 100-300줄로 분산
- 중복 코드 제거
- 단일 책임 원칙 적용

### **유지보수성**
- 기능별 독립적 수정 가능
- 테스트 용이성 향상
- 새 기능 추가 시 영향 범위 최소화

### **성능**
- 데이터베이스 연결 풀 사용
- 메모리 사용량 최적화
- 응답 시간 개선

## 🚀 **다음 단계**
1. **2단계 진행**: 공통 모듈 구축부터 시작
2. **점진적 마이그레이션**: 한 번에 하나씩 모듈 이전
3. **병렬 테스트**: 기존 시스템과 동시 운영하며 검증
