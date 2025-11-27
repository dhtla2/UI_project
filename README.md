# 🚢 Port Data Quality Dashboard

항만 운영 데이터의 품질 관리 및 모니터링을 위한 통합 대시보드 시스템

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19.1-61DAFB?style=flat&logo=react&logoColor=black)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.9-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

---

## 📋 목차

- [프로젝트 개요](#-프로젝트-개요)
- [주요 기능](#-주요-기능)
- [시스템 아키텍처](#-시스템-아키텍처)
- [기술 스택](#️-기술-스택)
- [프로젝트 구조](#-프로젝트-구조)
- [설치 및 실행](#-설치-및-실행)
- [환경 변수 설정](#-환경-변수-설정)
- [API 문서](#-api-문서)
- [개발 가이드](#-개발-가이드)
- [트러블슈팅](#-트러블슈팅)

---

## 🎯 프로젝트 개요

**Port Data Quality Dashboard**는 항만 운영에 필요한 다양한 데이터 소스(AIS, TOS, TC, QC, PMIS 등)의 **품질을 자동으로 검사**하고, **실시간으로 모니터링**할 수 있는 웹 기반 대시보드 시스템입니다.

### 핵심 가치

- 🔍 **데이터 품질 검사**: 완전성, 유효성, 일관성 자동 검증
- 📊 **실시간 모니터링**: 7가지 데이터 소스 통합 대시보드
- 🎨 **직관적 시각화**: Chart.js 기반의 인터랙티브 차트
- 🔄 **히스토리 추적**: 검사 이력 및 품질 추이 분석
- ⚡ **고성능**: FastAPI + React로 빠른 응답 속도

---

## ✨ 주요 기능

### 📡 **AIS (선박 자동식별시스템) 대시보드**
- 실시간 선박 위치 및 운항 정보 모니터링
- 선박 타입별/국적별 분포 시각화
- 위치 유효성 검사 (GRID 기반 육지/바다 검증)
- 필드별 완전성 및 데이터 품질 분석

### 🏗️ **TOS (터미널 운영 시스템) 대시보드**
- 접안 일정(Berth Schedule) 데이터 품질 검사
- 완전성 검사: 21개 필수 필드 검증
- 유효성 검사: 날짜 차이 검증 (ATD-ATA <= D3)
- 필드별 상세 분석 및 이슈 추적

### 🚛 **TC (터미널 컨테이너) 작업 대시보드**
- 터미널 작업 정보 모니터링
- 작업 유형별/터미널별 통계
- 데이터 일관성 검사
- 작업 히스토리 및 추이 분석

### 📦 **QC (품질 관리) 대시보드**
- 품질 검사 결과 통합 관리
- 검사 항목별 통과율 분석
- 이상 데이터 탐지 및 알림

### 📋 **PMIS (항만 관리 정보 시스템) 대시보드**
- 항만 운영 데이터 통합 모니터링
- KPI 지표 시각화

### 🚢 **선박 제원 정보 대시보드**
- 선박 기본 정보 조회 및 관리
- 선박 제원 데이터 품질 검증

### 📊 **통합 품질 관리 기능**
- **자동 검사**: 완전성(Completeness), 유효성(Validity), 일관성(Consistency)
- **실시간 알림**: 품질 기준 미달 시 자동 알림
- **검사 히스토리**: 일별/주별/월별 검사 이력 조회
- **필드별 분석**: 개별 필드의 품질 상세 분석

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    사용자 브라우저                            │
│                  (React + TypeScript)                        │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST API
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              Express.js (프로덕션 서버)                       │
│                   PORT: 4000                                │
│         - Build 파일 서빙                                     │
│         - API 프록시 (→ Backend)                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│           FastAPI 백엔드 서버 (Python)                        │
│                   PORT: 3000                                │
│  ┌─────────────┬──────────────┬───────────────────────┐    │
│  │ AIS Routes  │  TOS Routes  │  TC/QC/PMIS Routes    │    │
│  └─────────────┴──────────────┴───────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Data Inspection Service                      │   │
│  │   (완전성/유효성/일관성 검사 엔진)                      │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ↓                         ↓
┌──────────────────┐      ┌──────────────────┐
│  MySQL Database  │      │ SQLite Database  │
│   PORT: 3307     │      │ ais_database.db  │
│                  │      │                  │
│ - AIS Info       │      │ - AIS Legacy     │
│ - Berth Schedule │      │   Data           │
│ - TC Work Info   │      └──────────────────┘
│ - Inspection     │
│   Results        │
│ - UI Logs        │
└──────────────────┘
```

### 데이터 흐름

1. **Frontend** → API 요청 (Axios)
2. **Express Server** → FastAPI로 프록시
3. **FastAPI** → 라우터별 처리 (routers/)
4. **Service Layer** → 비즈니스 로직 실행 (services/)
5. **Database** → 데이터 조회/저장
6. **Inspection Engine** → 품질 검사 수행
7. **Response** → JSON 형태로 클라이언트 반환

---

## 🛠️ 기술 스택

### Frontend

| 기술 | 버전 | 용도 |
|------|------|------|
| **React** | 19.1.0 | UI 프레임워크 |
| **TypeScript** | 4.9.5 | 정적 타입 검사 |
| **Chart.js** | 4.5.0 | 데이터 시각화 |
| **Recharts** | 3.1.2 | 고급 차트 라이브러리 |
| **Axios** | 1.10.0 | HTTP 클라이언트 |
| **React Router** | - | SPA 라우팅 |
| **Express.js** | 5.1.0 | 프로덕션 서버 |

### Backend

| 기술 | 버전 | 용도 |
|------|------|------|
| **Python** | 3.11+ | 백엔드 언어 |
| **FastAPI** | 0.104.1 | 웹 프레임워크 |
| **Uvicorn** | 0.24.0 | ASGI 서버 |
| **Pydantic** | 2.5.0 | 데이터 검증 |
| **PyMySQL** | 1.1.0 | MySQL 드라이버 |
| **Pandas** | 2.2.0+ | 데이터 분석 |
| **NumPy** | 1.26.0+ | 수치 연산 |

### Database

| 기술 | 버전 | 용도 |
|------|------|------|
| **MySQL** | 8.0+ | 메인 데이터베이스 (port 3307) |
| **SQLite** | 3.x | AIS 레거시 데이터 |

### DevOps & Tools

- **Git** - 버전 관리
- **uv** - Python 패키지 관리
- **npm** - Node.js 패키지 관리
- **nohup** - 백그라운드 프로세스 관리

---

## 📁 프로젝트 구조

```
UI_project/
├── backend/                        # FastAPI 백엔드
│   ├── main.py                    # 메인 애플리케이션 (PORT: 3000)
│   ├── main_old.py                # 구버전 백업
│   ├── main_new.py                # 신버전 (개발 중)
│   ├── requirements.txt           # Python 의존성
│   ├── routers/                   # API 라우터
│   │   ├── ais_routes.py         # AIS API (733 lines)
│   │   ├── tos_routes.py         # TOS API
│   │   ├── tc_routes.py          # TC API
│   │   ├── qc_routes.py          # QC API
│   │   └── pmis_routes.py        # PMIS API
│   ├── services/                  # 비즈니스 로직
│   │   ├── ais_service.py        # AIS 데이터 서비스
│   │   └── ...
│   ├── models/                    # 데이터 모델
│   ├── config/                    # 설정 파일
│   │   └── settings.py           # 앱 설정
│   └── utils/                     # 유틸리티
│       └── helpers.py            # 헬퍼 함수
│
├── dashboard/                      # React 프론트엔드
│   ├── public/                    # 정적 파일
│   ├── src/
│   │   ├── components/           # React 컴포넌트
│   │   │   ├── AISPage.tsx       # AIS 대시보드
│   │   │   ├── TOSPage.tsx       # TOS 대시보드
│   │   │   ├── TCPage.tsx        # TC 대시보드
│   │   │   ├── QCPage.tsx        # QC 대시보드
│   │   │   ├── PMISPage.tsx      # PMIS 대시보드
│   │   │   ├── ShipInfoPage.tsx  # 선박제원 대시보드
│   │   │   ├── common/           # 공통 컴포넌트
│   │   │   │   ├── CommonMiddleSection.tsx
│   │   │   │   └── ...
│   │   │   └── charts/           # 차트 컴포넌트
│   │   ├── services/             # API 서비스
│   │   │   └── apiService.ts     # API 통신 레이어
│   │   ├── types/                # TypeScript 타입
│   │   └── App.tsx               # 루트 컴포넌트
│   ├── build/                     # 프로덕션 빌드 (생성됨)
│   ├── server.js                  # Express 프로덕션 서버
│   ├── package.json               # Node.js 의존성
│   └── tsconfig.json              # TypeScript 설정
│
├── db/                             # 데이터베이스 관련
│   ├── ais_service.py             # AIS 데이터 서비스
│   ├── ui_data_service.py         # UI 로그 서비스
│   ├── database_config.py         # MySQL 설정
│   ├── init_mysql_database.py     # DB 초기화
│   ├── data_inspection_service.py # 품질 검사 서비스
│   ├── sync_service/              # 데이터 동기화
│   └── README_MYSQL.md            # MySQL 가이드
│
├── .gitignore                      # Git 제외 파일
├── pyproject.toml                  # Python 프로젝트 설정
├── uv.lock                         # Python 의존성 잠금
├── ais_database.db                 # SQLite DB (레거시)
├── restart_backend.sh              # 백엔드 재시작 스크립트
├── QUICK_SETUP.sh                  # 빠른 설정 스크립트
└── README.md                       # 프로젝트 문서 (본 파일)
```

---

## 🚀 설치 및 실행

### 📋 사전 요구사항

- **Node.js** 18.x 이상
- **Python** 3.11 이상
- **MySQL** 8.0 이상 (PORT: 3307)
- **Git**
- **npm** 또는 **yarn**
- **uv** (Python 패키지 관리, 선택사항)

---

### 1️⃣ 프로젝트 클론

```bash
git clone https://github.com/dhtla2/UI_project.git
cd UI_project
```

---

### 2️⃣ MySQL 데이터베이스 설정

#### MySQL 설치 (Ubuntu/Debian 기준)

```bash
# MySQL 설치
sudo apt update
sudo apt install mysql-server

# MySQL 보안 설정
sudo mysql_secure_installation

# MySQL 시작
sudo systemctl start mysql
sudo systemctl enable mysql
```

#### 데이터베이스 생성 및 초기화

```bash
# MySQL 접속
mysql -u root -p

# 데이터베이스 생성
CREATE DATABASE port_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 사용자 생성 및 권한 부여
CREATE USER 'port_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON port_database.* TO 'port_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 초기 테이블 생성

```bash
cd db
python init_mysql_database.py
```

자세한 MySQL 설정은 [`db/README_MYSQL.md`](db/README_MYSQL.md)를 참조하세요.

---

### 3️⃣ 백엔드 설정 및 실행

#### 방법 A: Python venv 사용

```bash
cd backend

# 가상환경 생성
python -m venv .venv

# 가상환경 활성화
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt

# 백엔드 실행
python main_new.py
```

#### 방법 B: uv 사용 (권장)

```bash
cd backend

# uv로 의존성 설치
uv sync

# 백엔드 실행
uv run python main_new.py
```

#### 백그라운드 실행

```bash
# nohup으로 백그라운드 실행
nohup python main_new.py > backend.log 2>&1 &

# 또는 재시작 스크립트 사용
./restart_backend.sh
```

**백엔드 서버**: `http://localhost:3000`

**API 문서 (Swagger)**: `http://localhost:3000/docs`

---

### 4️⃣ 프론트엔드 설정 및 실행

#### 개발 모드 (Hot Reload)

```bash
cd dashboard

# 의존성 설치
npm install

# 개발 서버 실행
npm start
```

**개발 서버**: `http://localhost:8000`

#### 프로덕션 모드 (Express 서버)

```bash
cd dashboard

# 프로덕션 빌드
npm run build

# Express 서버로 실행
npm run start:express
# 또는
node server.js
```

**프로덕션 서버**: `http://localhost:4000`

#### 백그라운드 실행

```bash
cd dashboard

# 빌드 후 백그라운드 실행
npm run build
nohup node server.js > ../nohup.out 2>&1 &

# 프로세스 확인
ps aux | grep "node server.js"

# 종료
pkill -f "node server.js"
```

---

### 5️⃣ 빠른 설정 (All-in-One)

```bash
# 전체 시스템 설정 및 실행
./QUICK_SETUP.sh
```

이 스크립트는 다음을 자동으로 수행합니다:
1. MySQL 데이터베이스 초기화
2. 백엔드 의존성 설치 및 실행
3. 프론트엔드 빌드 및 실행

---

## 🔧 환경 변수 설정

### Backend (`backend/config/settings.py`)

```python
# MySQL 데이터베이스 설정
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'root',
    'password': 'Password',
    'database': 'port_database',
    'charset': 'utf8mb4'
}

# SQLite 데이터베이스 경로
ais_db_path: str = "../ais_database.db"

# 서버 설정
HOST = "0.0.0.0"
PORT = 3000
```

### Frontend (`dashboard/.env`)

```bash
# API 엔드포인트
REACT_APP_API_URL=http://localhost:3000

# 프로덕션 API (외부 서버)
# REACT_APP_API_URL=http://203.253.128.186:8000
```

### Express Server (`dashboard/server.js`)

```javascript
const PORT = 4000;  // 프로덕션 서버 포트
const API_TARGET = 'http://localhost:3000';  // 백엔드 API
```

---

## 📡 API 문서

### 엔드포인트 개요

FastAPI는 자동으로 Swagger UI를 생성합니다:
- **Swagger UI**: `http://localhost:3000/docs`
- **ReDoc**: `http://localhost:3000/redoc`

### 주요 API 엔드포인트

#### 🔹 AIS (선박 정보)

```http
GET  /api/dashboard/ais-summary
GET  /api/dashboard/ais-quality-summary
GET  /api/dashboard/ais-quality-details
GET  /api/dashboard/ais-charts
GET  /api/dashboard/ais-inspection-history?period=daily&start_date=2025-10-01&end_date=2025-10-31
GET  /api/dashboard/data-quality-status
```

#### 🔹 TOS (터미널 운영)

```http
GET  /api/dashboard/tos-quality-summary
GET  /api/dashboard/tos-quality-details
GET  /api/dashboard/tos-field-analysis
GET  /api/dashboard/tos-inspection-history?period=monthly
GET  /api/dashboard/tos-data-quality-status
```

#### 🔹 TC (터미널 컨테이너)

```http
GET  /api/dashboard/tc-summary
GET  /api/dashboard/tc-quality-summary
GET  /api/dashboard/tc-quality-status
GET  /api/dashboard/tc-inspection-history?period=weekly
GET  /api/dashboard/tc-work-history
```

#### 🔹 QC (품질 관리)

```http
GET  /api/dashboard/qc-summary
GET  /api/dashboard/qc-quality-summary
GET  /api/dashboard/qc-quality-status
GET  /api/dashboard/qc-inspection-history
```

#### 🔹 PMIS (항만 관리)

```http
GET  /api/dashboard/pmis-summary
GET  /api/dashboard/pmis-quality-summary
```

#### 🔹 검사 히스토리 기간 옵션

- `period=daily`: 일별 (기본: 최근 14일)
- `period=weekly`: 주별
- `period=monthly`: 월별
- `period=custom`: 사용자 지정 (`start_date`, `end_date` 필수)

### API 응답 예시

#### AIS 품질 요약

```json
{
  "total_inspections": 150,
  "total_checks": 2500,
  "pass_count": 2350,
  "fail_count": 150,
  "pass_rate": 94.0,
  "last_inspection_date": "2025-10-21",
  "completeness": {
    "fields_checked": 1500,
    "pass_count": 1450,
    "fail_count": 50,
    "pass_rate": 96.7
  },
  "validity": {
    "fields_checked": 1000,
    "pass_count": 900,
    "fail_count": 100,
    "pass_rate": 90.0
  }
}
```

---

## 💻 개발 가이드

### 브랜치 전략

```
main
  ├─ feat/new-feature        # 새 기능 개발
  ├─ fix/bug-fix             # 버그 수정
  ├─ chore/cleanup           # 코드 정리
  └─ refactor/optimization   # 리팩토링
```

### 커밋 메시지 규칙

```bash
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 코드 리팩토링
chore: 빌드/설정 변경
test: 테스트 추가/수정
perf: 성능 개선
```

### 개발 워크플로우

1. **브랜치 생성**
   ```bash
   git checkout -b feat/new-dashboard
   ```

2. **코드 작성 및 테스트**
   ```bash
   # 백엔드 테스트
   cd backend && python -m pytest

   # 프론트엔드 테스트
   cd dashboard && npm test
   ```

3. **커밋 및 푸시**
   ```bash
   git add .
   git commit -m "feat: TC 대시보드 검사 히스토리 추가"
   git push -u origin feat/new-dashboard
   ```

4. **Pull Request 생성**
   - GitHub에서 PR 생성
   - 코드 리뷰 진행
   - main 브랜치로 병합

### 코드 스타일

#### Python (Backend)

```python
# PEP 8 준수
# 함수/변수: snake_case
# 클래스: PascalCase
# 상수: UPPER_CASE

def fetch_inspection_history(period: str = 'daily') -> List[Dict]:
    """검사 히스토리 조회
    
    Args:
        period: 조회 기간 (daily, weekly, monthly, custom)
        
    Returns:
        검사 히스토리 리스트
    """
    pass
```

#### TypeScript (Frontend)

```typescript
// 함수/변수: camelCase
// 인터페이스/타입: PascalCase
// 상수: UPPER_CASE

interface InspectionHistoryData {
  date: string;
  score: number;
  totalChecks: number;
}

const fetchInspectionHistory = async (
  period: 'daily' | 'weekly' | 'monthly' = 'daily'
): Promise<InspectionHistoryData[]> => {
  // ...
};
```

---

## 🔍 트러블슈팅

### 1. 백엔드 실행 오류

#### ❌ `ModuleNotFoundError: No module named 'fastapi'`

```bash
# 의존성 재설치
pip install -r requirements.txt

# 또는 uv 사용
uv sync
```

#### ❌ `Can't connect to MySQL server on 'localhost:3307'`

```bash
# MySQL 실행 확인
sudo systemctl status mysql

# MySQL 재시작
sudo systemctl restart mysql

# 포트 확인
sudo netstat -tulpn | grep 3307
```

### 2. 프론트엔드 빌드 오류

#### ❌ `npm ERR! missing script: build`

```bash
# package.json 확인
cat dashboard/package.json | grep scripts

# node_modules 재설치
cd dashboard
rm -rf node_modules package-lock.json
npm install
```

#### ❌ 빌드 후 페이지가 빈 화면

```bash
# build 디렉토리 확인
ls -la dashboard/build/

# 빌드 재실행
cd dashboard
npm run build

# Express 서버 재시작
pkill -f "node server.js"
nohup node server.js > ../nohup.out 2>&1 &
```

### 3. API 호출 실패

#### ❌ `CORS policy error`

```javascript
// dashboard/server.js에서 CORS 설정 확인
app.use(cors({
  origin: '*',
  credentials: true
}));
```

#### ❌ `Network Error` 또는 `ERR_CONNECTION_REFUSED`

```bash
# 백엔드 실행 확인
ps aux | grep "python main.py"

# 백엔드 로그 확인
tail -f backend.log

# 백엔드 재시작
cd backend
python main_new.py
```

### 4. 데이터베이스 연결 오류

#### ❌ `Access denied for user 'root'@'localhost'`

```python
# backend/config/settings.py 확인
MYSQL_CONFIG = {
    'user': 'root',
    'password': 'YOUR_CORRECT_PASSWORD',  # 비밀번호 확인
    # ...
}
```

#### ❌ `Unknown database 'port_database'`

```bash
# 데이터베이스 생성
mysql -u root -p
CREATE DATABASE port_database;

# 또는 초기화 스크립트 실행
cd db
python init_mysql_database.py
```

### 5. 백그라운드 프로세스 관리

#### 프로세스 확인

```bash
# 백엔드 프로세스
ps aux | grep "python main.py"

# 프론트엔드 프로세스
ps aux | grep "node server.js"
```

#### 프로세스 종료

```bash
# 특정 프로세스 종료
kill -9 <PID>

# 모든 관련 프로세스 종료
pkill -f "python main.py"
pkill -f "node server.js"
```

#### 재시작

```bash
# 백엔드 재시작
./restart_backend.sh

# 프론트엔드 재시작
cd dashboard
pkill -f "node server.js"
nohup node server.js > ../nohup.out 2>&1 &
```

---

## 📚 추가 문서

- [MySQL 설정 가이드](db/README_MYSQL.md)
- [AIS 데이터베이스 아키텍처](AIS_DATABASE_ARCHITECTURE.md)
- [로그인 통합 가이드](README_LOGIN_INTEGRATION.md)
- [데이터베이스 업데이트 로그](db/README_DB_UPDATE.md)
- [동기화 서비스 가이드](db/README_UPDATED_SYNC_SERVICE.md)

---

## 📄 라이선스

이 프로젝트는 **MIT 라이선스** 하에 배포됩니다.

---

## 📞 문의 및 지원

- **이슈 리포트**: [GitHub Issues](https://github.com/dhtla2/UI_project/issues)

---