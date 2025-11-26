# API 엔드포인트 분석 및 모듈 매핑

## 📊 **엔드포인트 분류**

### 🏠 **Common/Root Routes** (`routers/common_routes.py`)
- `GET /` - 루트 엔드포인트
- `GET /api/dashboard/health` - 헬스 체크
- `POST /api/quality-check/run` - 품질 검사 실행
- `GET /api/quality-check/history` - 품질 검사 히스토리 조회

### 🚢 **AIS Routes** (`routers/ais_routes.py`)
- `GET /ais/all` - 모든 AIS 데이터 조회
- `GET /ais/mmsi/{mmsi}` - MMSI로 선박 검색
- `GET /ais/name/{name}` - 선박명으로 검색
- `GET /ais/flag/{flag}` - 국적별 선박 검색
- `GET /ais/type/{ship_type}` - 선박 타입별 필터링
- `GET /ais/latest` - 최신 데이터 조회
- `GET /ais/statistics` - 통계 데이터 조회
- `GET /api/dashboard/ais-summary` - AIS 데이터 요약 조회
- `GET /api/dashboard/ais-quality-status` - AIS 품질 상태 데이터 조회
- `GET /api/dashboard/ais-quality-summary` - AIS 데이터 품질 요약 정보
- `GET /api/dashboard/ais-quality-details` - AIS 데이터 품질 상세 분석
- `GET /api/dashboard/ais-charts` - AIS 차트 데이터
- `GET /api/dashboard/ais-inspection-history` - AIS 검사 히스토리

### 🏗️ **TOS Routes** (`routers/tos_routes.py`)
- `GET /api/dashboard/tos-quality-details` - TOS 품질 상세 데이터
- `GET /api/dashboard/tos-quality-summary` - TOS 품질 요약 데이터
- `GET /api/dashboard/tos-field-analysis` - TOS 필드별 상세 분석 데이터
- `GET /api/dashboard/tos-inspection-history` - TOS 검사 히스토리
- `GET /api/dashboard/tos-data-quality-status` - TOS 데이터 품질 상태

### 🏗️ **TC Routes** (`routers/tc_routes.py`)
- `GET /api/dashboard/tc-quality-summary` - TC 품질 요약 데이터
- `GET /api/dashboard/tc-summary` - TC 작업 요약 정보
- `GET /api/dashboard/tc-work-history` - TC 작업 히스토리
- `GET /api/dashboard/tc-quality-status` - TC 데이터 품질 상태

### 🔍 **QC Routes** (`routers/qc_routes.py`)
- `GET /api/dashboard/qc-quality-summary` - QC 품질 요약 데이터
- `GET /api/dashboard/qc-quality-status` - QC 데이터 품질 상태
- `GET /api/dashboard/qc-summary` - QC 작업 요약 데이터
- `GET /api/dashboard/qc-work-history` - QC 작업 히스토리 데이터

### 📊 **Dashboard Routes** (`routers/dashboard_routes.py`)
- `GET /api/dashboard/latest-inspection-results` - 최신 검사 결과 조회
- `GET /api/dashboard/recent-inspections` - 최근 검사 결과 조회
- `GET /api/dashboard/quality-metrics` - 품질 메트릭 요약 조회
- `GET /api/dashboard/data-source-stats` - 데이터 소스별 통계 조회
- `GET /api/dashboard/performance-trends` - 성능 트렌드 데이터 조회
- `GET /api/dashboard/api-quality` - API 품질 데이터 조회
- `GET /api/dashboard/data-quality-status` - 데이터 품질 상태 및 알림 정보
- `GET /api/dashboard/failed-items` - 실패한 항목 데이터 조회

### 👤 **UI/User Routes** (`routers/ui_routes.py`)
- `POST /ui/log/page-visit` - 페이지 방문 로그 저장
- `GET /ui/statistics` - UI 통계 데이터 조회
- `GET /ui/user/{user_id}/activity` - 특정 사용자의 활동 요약
- `GET /ui/logs/page-visits` - 페이지 방문 로그 조회
- `GET /ui/logs/api-calls` - API 호출 로그 조회
- `GET /ui/statistics/visitor-trends` - 방문자 트렌드 분석 데이터 조회
- `GET /ui/statistics/time-based` - 시간별 통계 데이터 조회

## 🏗️ **서비스 레이어 분류**

### `services/database.py`
- 데이터베이스 연결 관리
- 공통 쿼리 유틸리티

### `services/ais_service.py`
- AIS 데이터 조회 로직
- AIS 통계 계산
- AIS 품질 분석

### `services/tos_service.py`
- TOS 데이터 조회 로직
- TOS 품질 분석
- TOS 필드 분석

### `services/tc_service.py`
- TC 작업 데이터 처리
- TC 품질 분석

### `services/qc_service.py`
- QC 작업 데이터 처리

### `services/inspection_service.py`
- 검사 히스토리 관리
- 검사 결과 분석

### `services/ui_service.py`
- UI 통계 처리
- 사용자 활동 로그 관리

### `services/quality_service.py`
- 데이터 품질 분석
- 품질 메트릭 계산
- 품질 검사 실행 로직

## 📁 **모델 및 설정**

### `models/schemas.py`
- 모든 Pydantic 모델 정의
- 요청/응답 스키마

### `config/database.py`
- 데이터베이스 설정
- 연결 풀 관리

### `config/settings.py`
- 환경 변수 관리
- 애플리케이션 설정

### `utils/helpers.py`
- 공통 유틸리티 함수
- 날짜/시간 처리
- 데이터 변환 함수

## 📊 **통계 요약**
- **총 엔드포인트**: 42개
- **Common 관련**: 4개 (루트, 헬스체크, 품질검사 2개)
- **AIS 관련**: 12개
- **TOS 관련**: 5개
- **TC 관련**: 4개
- **QC 관련**: 4개 (품질검사 제외)
- **Dashboard 관련**: 8개
- **UI 관련**: 7개
