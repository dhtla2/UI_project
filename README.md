# AIS 선박 데이터 대시보드

AIS(선박 자동식별시스템) 데이터를 시각화하는 React 기반 대시보드입니다.

## 🚀 기능

- **실시간 데이터 시각화**: Chart.js를 활용한 다양한 차트
- **선박 타입별 분포**: 파이 차트로 선박 타입별 통계
- **국적별 선박 분포**: 파이 차트로 국적별 선박 통계
- **속도 분포**: 바 차트로 선박 속도 분포
- **시간대별 활동**: 선형 차트로 시간대별 선박 활동 현황
- **통계 대시보드**: 전체 통계 정보 표시
- **최신 데이터 목록**: 실시간 선박 데이터 목록
- **반응형 디자인**: 모바일과 데스크톱 모두 지원

## 🛠️ 기술 스택

### Frontend
- **React 18** + **TypeScript**
- **Chart.js** + **react-chartjs-2** (데이터 시각화)
- **Axios** (API 통신)
- **CSS Grid** + **Flexbox** (레이아웃)

### Backend
- **FastAPI** (Python 웹 프레임워크)
- **PyMySQL** (MySQL 데이터베이스 연결)
- **Pydantic** (데이터 검증)

### Database
- **MySQL** (AIS 데이터 저장)

## 📁 프로젝트 구조

```
UI_project/
├── dashboard/                 # React 프론트엔드
│   ├── src/
│   │   ├── components/       # React 컴포넌트
│   │   │   ├── charts/       # 차트 컴포넌트들
│   │   │   ├── dashboard/    # 대시보드 컴포넌트들
│   │   │   └── layout/       # 레이아웃 컴포넌트들
│   │   ├── services/         # API 서비스
│   │   ├── types/            # TypeScript 타입 정의
│   │   └── App.tsx
│   └── package.json
├── backend/                  # FastAPI 백엔드
│   ├── main.py              # API 서버
│   └── requirements.txt     # Python 의존성
├── db/                      # 데이터베이스 관련
│   ├── ais_service.py       # AIS 데이터 서비스
│   ├── database_config.py   # MySQL 설정
│   ├── init_mysql_database.py # DB 초기화 스크립트
│   └── README_MYSQL.md      # MySQL 설정 가이드
├── filtered_ais_data.csv    # 샘플 데이터
└── README.md
```

## 🚀 설치 및 실행

### 1. MySQL 데이터베이스 설정

#### MySQL 설치
- **Windows**: [MySQL Community Server](https://dev.mysql.com/downloads/mysql/) 다운로드 및 설치
- **macOS**: `brew install mysql && brew services start mysql`
- **Linux**: `sudo apt install mysql-server` (Ubuntu/Debian)

#### 데이터베이스 초기화
```bash
# 1. 설정 파일 수정
# db/database_config.py에서 MySQL 연결 정보 수정

# 2. 데이터베이스 초기화
cd db
python init_mysql_database.py
```

자세한 설정 방법은 [MySQL 설정 가이드](db/README_MYSQL.md)를 참조하세요.

### 2. 백엔드 실행

```bash
cd backend
pip install -r requirements.txt
python main.py
```

FastAPI 서버가 `http://localhost:8000`에서 실행됩니다.

### 3. 프론트엔드 실행

```bash
cd dashboard
npm install
npm start
```

React 앱이 `http://localhost:3000`에서 실행됩니다.

## 📊 API 엔드포인트

### 데이터 조회
- `GET /ais/all` - 모든 AIS 데이터 조회
- `GET /ais/latest` - 최신 데이터 조회
- `GET /ais/mmsi/{mmsi}` - MMSI로 선박 검색
- `GET /ais/name/{name}` - 선박명으로 검색
- `GET /ais/flag/{flag}` - 국적별 선박 검색
- `GET /ais/type/{ship_type}` - 선박 타입별 필터링

### 통계
- `GET /ais/statistics` - 통계 데이터 조회

## 🎨 대시보드 구성

1. **시간대별 선박 활동 현황 (선형 차트)**
   - 6시간 단위로 선박 활동 현황 표시
   - UTC 시간 기준으로 데이터 그룹화

2. **선박 타입별 분포 (파이 차트)**
   - 선박 타입별 개수와 비율
   - 상위 10개 타입 표시

3. **국적별 선박 분포 (파이 차트)**
   - 국적별 선박 개수와 비율
   - 상위 10개 국적 표시

4. **선박 속도 분포 (바 차트)**
   - 속도 범위별 선박 개수
   - 0-5, 5-10, 10-15, 15-20, 20-25, 25+ knots

5. **통계 대시보드**
   - 총 선박 수, 선박 타입 수, 국적 수, 항해 상태 수

6. **최신 선박 데이터 목록**
   - 최신 10개 선박 데이터 표시
   - 선박명, 타입, 국적, 속도, 시간 정보

## 🔧 개발 환경 설정

### Node.js 설치
- Node.js 18+ 버전 필요
- [Node.js 공식 사이트](https://nodejs.org/)에서 다운로드

### Python 설치
- Python 3.11+ 버전 필요
- [Python 공식 사이트](https://python.org/)에서 다운로드

### MySQL 설치
- MySQL 8.0+ 버전 권장
- [MySQL 공식 사이트](https://mysql.com/)에서 다운로드

## 📝 데이터 구조

AIS 데이터는 다음과 같은 주요 필드를 포함합니다:

- **기본 정보**: MMSI, IMO, 선박명, 호출부호
- **선박 정보**: 타입, 길이, 폭, 국적
- **위치 정보**: 경도, 위도
- **항해 정보**: 속도, 방향, 회전율, 헤딩
- **상태 정보**: 항해 상태, 목적지, ETA

## 🔄 데이터 연동

이 프로젝트는 `db/ais_service.py`를 통해 MySQL 데이터베이스의 AIS 데이터를 실시간으로 조회하여 대시보드에 표시합니다:

- **실시간 데이터 로딩**: 각 차트 컴포넌트가 API를 통해 실시간 데이터 조회
- **로딩 상태 관리**: 데이터 로딩 중 로딩 표시
- **에러 처리**: API 오류 시 에러 메시지 표시
- **자동 새로고침**: 컴포넌트 마운트 시 자동으로 데이터 갱신

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.
