# AIS 대시보드 데이터베이스 아키텍처

## 📊 **개요**
AIS 대시보드는 **2개의 데이터베이스**를 사용하여 운영됩니다:
- **SQLite** (`ais_database.db`): AIS 원본 데이터 저장
- **MySQL** (`port_database`): 데이터 품질 검사 결과 저장

---

## 🗄️ **데이터베이스 1: SQLite (AIS 원본 데이터)**

### 위치
- **파일**: `/home/cotlab/UI_project_new/ais_database.db`
- **연결**: `DatabaseService.execute_ais_query()`

### 테이블: `ais_info`

#### 주요 컬럼
```sql
- mmsiNo          -- MMSI 번호
- vsslNm          -- 선박명
- vsslTp          -- 선박 타입
- flag            -- 국적
- vsslNavi        -- 항해 상태
- sog             -- 속도 (Speed Over Ground)
- cog             -- 방향 (Course Over Ground)
- lat             -- 위도
- lon             -- 경도
- heading         -- 선수방향
- rot             -- 회전율
- navStatus       -- 항해 상태 코드
- ... (기타 AIS 필드)
```

#### 사용처
| 엔드포인트 | 테이블 | 쿼리 용도 |
|-----------|-------|----------|
| `/api/dashboard/ais/all` | `ais_info` | 전체 AIS 데이터 조회 |
| `/api/dashboard/ais/mmsi/{mmsi}` | `ais_info` | MMSI로 선박 검색 |
| `/api/dashboard/ais/name/{name}` | `ais_info` | 선박명으로 검색 |
| `/api/dashboard/ais/flag/{flag}` | `ais_info` | 국적별 선박 검색 |
| `/api/dashboard/ais/statistics` | `ais_info` | 선박 타입별/국적별/항해상태별 통계 |
| `/api/dashboard/ais-summary` | `ais_info` | 총 선박 수, 선박 타입 분포, 국적 분포 |
| `/api/dashboard/ais-charts` | `ais_info` | 차트용 데이터 (선박타입, 국적, 속도 분포) |

#### 주요 쿼리 예시

**1. 선박 타입별 통계**
```sql
SELECT vsslTp, COUNT(*) as count 
FROM ais_info 
WHERE vsslTp IS NOT NULL 
GROUP BY vsslTp 
ORDER BY count DESC 
LIMIT 10
```

**2. 국적별 통계**
```sql
SELECT flag, COUNT(*) as count 
FROM ais_info 
WHERE flag IS NOT NULL 
GROUP BY flag 
ORDER BY count DESC 
LIMIT 10
```

**3. 속도 분포**
```sql
SELECT 
    CASE 
        WHEN sog < 5 THEN '0-5 knots'
        WHEN sog < 10 THEN '5-10 knots'
        WHEN sog < 15 THEN '10-15 knots'
        WHEN sog < 20 THEN '15-20 knots'
        ELSE '20+ knots'
    END as speed_range,
    COUNT(*) as count
FROM ais_info 
WHERE sog IS NOT NULL AND sog >= 0
GROUP BY speed_range
```

---

## 🗄️ **데이터베이스 2: MySQL (품질 검사 결과)**

### 연결 정보
- **호스트**: `localhost`
- **포트**: `3307`
- **데이터베이스**: `port_database`
- **사용자**: `root`
- **비밀번호**: `Keti1234!`

### 테이블 1: `data_inspection_results`

#### 스키마
```sql
CREATE TABLE data_inspection_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100) NOT NULL,           -- 검사 ID (예: ais_info_inspection_xxx)
    check_type VARCHAR(50) NOT NULL,               -- 검사 타입 (completeness, validity, etc)
    check_name VARCHAR(100) NOT NULL,              -- 검사명
    message TEXT NOT NULL,                         -- 검사 메시지
    status ENUM('PASS','FAIL','WARNING','ERROR'),  -- 검사 상태
    severity ENUM('LOW','MEDIUM','HIGH','CRITICAL'), -- 심각도
    affected_rows INT DEFAULT 0,                   -- 영향받은 행 수
    affected_columns LONGTEXT,                     -- 영향받은 컬럼 (JSON)
    details LONGTEXT,                              -- 상세 정보 (JSON)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_check_type (check_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

#### 사용처
| 엔드포인트 | 테이블 | 쿼리 용도 |
|-----------|-------|----------|
| `/api/dashboard/ais-summary` | `data_inspection_results` | 총 검사 횟수, PASS 개수, 마지막 검사 일시 |
| `/api/dashboard/ais-quality-status` | `data_inspection_results` | 전체/완전성/유효성 품질 통계 |
| `/api/dashboard/ais-quality-details` | `data_inspection_results` | 최근 검사 결과 상세, 검사 타입별 통계, 실패 원인 분석 |
| `/api/dashboard/ais-inspection-history` | `data_inspection_results` | 기간별 검사 히스토리 (일별/주별/월별) |
| `/api/dashboard/latest-inspection-results` | `data_inspection_results` | 최신 검사 결과 (완전성, 유효성) |
| `/api/dashboard/ais-field-analysis` | `data_inspection_results` | 필드별 품질 분석 (오류율, 영향받은 행 수) |
| `/api/dashboard/failed-items` | `data_inspection_results` | 실패한 검사 항목 목록 |

#### 주요 쿼리 예시

**1. 품질 요약 (전체)**
```sql
SELECT 
    COUNT(DISTINCT inspection_id) as total_inspections,
    COUNT(*) as total_checks,
    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
    MAX(created_at) as last_inspection
FROM data_inspection_results 
WHERE inspection_id LIKE '%ais_info_inspection%'
```

**2. 완전성 검사 통계**
```sql
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count
FROM data_inspection_results 
WHERE inspection_id LIKE '%ais_info_inspection%' 
    AND check_type = 'completeness'
```

**3. 유효성 검사 통계**
```sql
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count
FROM data_inspection_results 
WHERE inspection_id LIKE '%ais_info_inspection%' 
    AND check_type = 'validity'
```

**4. 일별 검사 히스토리**
```sql
SELECT 
    DATE(created_at) as period_key,
    COUNT(*) as total_checks,
    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
    ROUND(SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pass_rate,
    SUM(CASE WHEN check_type = 'completeness' AND status = 'PASS' THEN 1 ELSE 0 END) as completeness_pass,
    SUM(CASE WHEN check_type = 'validity' AND status = 'PASS' THEN 1 ELSE 0 END) as validity_pass
FROM data_inspection_results 
WHERE inspection_id LIKE '%ais_info_inspection%'
GROUP BY DATE(created_at)
ORDER BY DATE(created_at) ASC
```

**5. 필드별 품질 분석**
```sql
SELECT 
    check_name as field_name,
    check_type,
    COUNT(*) as total_checks,
    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
    ROUND(SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pass_rate,
    MAX(affected_rows) as affected_rows,
    MAX(message) as last_message
FROM data_inspection_results
WHERE inspection_id LIKE '%ais_info_inspection%'
GROUP BY check_name, check_type
ORDER BY check_type, check_name
```

**6. 실패 원인 분석**
```sql
SELECT 
    check_name,
    message,
    COUNT(*) as failure_count
FROM data_inspection_results 
WHERE inspection_id LIKE '%ais_info_inspection%' 
    AND status = 'FAIL'
GROUP BY check_name, message
ORDER BY failure_count DESC
LIMIT 10
```

### 테이블 2: `data_inspection_info`

#### 스키마
```sql
CREATE TABLE data_inspection_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100) UNIQUE NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    data_source VARCHAR(50) NOT NULL,
    total_rows INT NOT NULL,
    total_columns INT NOT NULL,
    inspection_type VARCHAR(50) NOT NULL,
    inspection_status ENUM('pending','running','completed','failed'),
    start_time DATETIME,
    end_time DATETIME,
    processing_time_ms INT,
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_table_name (table_name),
    INDEX idx_data_source (data_source),
    INDEX idx_inspection_status (inspection_status),
    INDEX idx_created_at (created_at)
);
```

#### 사용처
- 검사 메타데이터 저장
- 검사 실행 이력 추적
- 처리 시간 및 상태 관리

### 테이블 3: `data_inspection_summary`

#### 스키마
```sql
CREATE TABLE data_inspection_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100) UNIQUE NOT NULL,
    total_checks INT NOT NULL,
    passed_checks INT NOT NULL,
    failed_checks INT NOT NULL,
    warning_checks INT NOT NULL,
    error_checks INT NOT NULL,
    pass_rate DECIMAL(5,2),
    data_quality_score DECIMAL(5,2),
    summary_json LONGTEXT,
    recommendations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_pass_rate (pass_rate),
    INDEX idx_data_quality_score (data_quality_score),
    INDEX idx_created_at (created_at)
);
```

#### 사용처
- 검사 결과 요약 정보 저장
- 품질 점수 관리
- 권장사항 저장

### 테이블 4: `api_response_data`

#### 스키마
```sql
CREATE TABLE api_response_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100) NOT NULL,
    data_source VARCHAR(50) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    raw_response_data LONGTEXT,
    processed_data_count INT,
    data_columns LONGTEXT,
    data_file_name VARCHAR(255),
    data_file_size_bytes BIGINT,
    data_checksum VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_data_source (data_source),
    INDEX idx_data_type (data_type),
    INDEX idx_created_at (created_at)
);
```

#### 사용처
- API 응답 원본 데이터 저장
- 데이터 컬럼 정보 저장
- 파일 메타데이터 저장

---

## 🔄 **프론트엔드 → 백엔드 → DB 데이터 흐름**

### 1. AIS 기본 정보 (선박 통계)
```
프론트엔드 (AISPage.tsx)
    ↓ fetchAISSummary()
백엔드 (/api/dashboard/ais-summary)
    ↓ get_ais_summary()
    ├─ SQLite: ais_info → 선박 통계
    └─ MySQL: data_inspection_results → 품질 정보
```

### 2. AIS 품질 상태
```
프론트엔드 (AISPage.tsx)
    ↓ fetchAISQualityStatus()
백엔드 (/api/dashboard/ais-quality-status)
    ↓ get_ais_quality_status()
MySQL: data_inspection_results
    ├─ 전체 품질 통계
    ├─ 완전성 검사 통계
    └─ 유효성 검사 통계
```

### 3. 검사 히스토리
```
프론트엔드 (AISPage.tsx)
    ↓ fetchAISInspectionHistory(period, start, end)
백엔드 (/api/dashboard/ais-inspection-history)
    ↓ get_ais_inspection_history()
MySQL: data_inspection_results
    └─ 기간별 (daily/weekly/monthly) 그룹화 쿼리
```

### 4. 최신 검사 결과
```
프론트엔드 (AISPage.tsx)
    ↓ fetchLatestInspectionResults('AIS')
백엔드 (/api/dashboard/latest-inspection-results)
    ↓ get_latest_inspection_results()
MySQL: data_inspection_results
    ├─ 완전성: pass_rate, total_checks, pass_count, fail_count
    └─ 유효성: pass_rate, total_checks, pass_count, fail_count
```

### 5. 필드별 분석
```
프론트엔드 (CommonFieldAnalysisSection.tsx)
    ↓ fetchAISFieldAnalysis()
백엔드 (/api/dashboard/ais-field-analysis)
    ↓ get_ais_field_analysis()
MySQL: data_inspection_results
    └─ 필드별 검사 통계 (field_name, check_type, pass_rate, affected_rows)
```

### 6. 차트 데이터
```
프론트엔드 (차트 컴포넌트)
    ↓ fetchAISChartsData()
백엔드 (/api/dashboard/ais-charts)
    ↓ get_ais_charts()
SQLite: ais_info
    ├─ 선박 타입별 분포
    ├─ 국적별 분포
    └─ 속도 분포
```

---

## 📋 **전체 엔드포인트 목록 (AIS)**

### AIS 데이터 조회 (SQLite)
| 엔드포인트 | 메소드 | 설명 | 테이블 |
|-----------|--------|------|--------|
| `/api/dashboard/ais/all` | GET | 전체 AIS 데이터 | `ais_info` |
| `/api/dashboard/ais/mmsi/{mmsi}` | GET | MMSI로 검색 | `ais_info` |
| `/api/dashboard/ais/name/{name}` | GET | 선박명으로 검색 | `ais_info` |
| `/api/dashboard/ais/flag/{flag}` | GET | 국적별 검색 | `ais_info` |
| `/api/dashboard/ais/statistics` | GET | 선박 통계 | `ais_info` |
| `/api/dashboard/ais-charts` | GET | 차트 데이터 | `ais_info` |

### 품질 검사 결과 (MySQL)
| 엔드포인트 | 메소드 | 설명 | 테이블 |
|-----------|--------|------|--------|
| `/api/dashboard/ais-summary` | GET | AIS 요약 (통계 + 품질) | `ais_info` + `data_inspection_results` |
| `/api/dashboard/ais-quality-status` | GET | 품질 상태 | `data_inspection_results` |
| `/api/dashboard/ais-quality-summary` | GET | 품질 요약 | `data_inspection_results` |
| `/api/dashboard/ais-quality-details` | GET | 품질 상세 분석 | `data_inspection_results` |
| `/api/dashboard/ais-inspection-history` | GET | 검사 히스토리 | `data_inspection_results` |
| `/api/dashboard/latest-inspection-results` | GET | 최신 검사 결과 | `data_inspection_results` |
| `/api/dashboard/ais-field-analysis` | GET | 필드별 분석 | `data_inspection_results` |
| `/api/dashboard/failed-items` | GET | 실패 항목 목록 | `data_inspection_results` |

---

## 🔍 **검사 ID 패턴**

AIS 관련 검사는 다음과 같은 패턴의 `inspection_id`를 사용합니다:
```
ais_info_inspection_{timestamp}_{random_hash}

예시:
- ais_info_inspection_1760578679_319e09
- ais_info_inspection_1760576944_c38bc7
```

모든 AIS 관련 쿼리는 다음 조건을 사용합니다:
```sql
WHERE inspection_id LIKE '%ais_info_inspection%'
```

---

## 📊 **주요 지표 계산 방식**

### 1. 통과율 (Pass Rate)
```python
pass_rate = (pass_count / total_checks) * 100
```

### 2. 완전성 비율 (Completeness Rate)
```python
completeness_rate = (completeness_pass / completeness_total) * 100
```

### 3. 유효성 비율 (Validity Rate)
```python
validity_rate = (validity_pass / validity_total) * 100
```

### 4. 데이터 품질 점수 (Data Quality Score)
```python
quality_score = (passed_checks / total_checks) * 100
```

---

## 🔧 **서비스 레이어 구조**

```
services/
├── database.py
│   ├── DatabaseService         # MySQL 연결 관리
│   ├── AISService              # AIS 데이터 조회 (SQLite)
│   └── UIDataService           # UI 통계 데이터
│
└── quality_service.py
    └── QualityService          # 품질 검사 로직
```

### DatabaseService
- **역할**: SQLite (`ais_database.db`) 연결 관리
- **메소드**: `execute_ais_query(query, params)`

### AISService
- **역할**: AIS 데이터 조회 및 필터링
- **메소드**:
  - `load_all_data(limit)` → `SELECT * FROM ais_info`
  - `load_by_mmsi(mmsi)` → `SELECT * FROM ais_info WHERE mmsiNo = ?`
  - `load_by_ship_name(name)` → `SELECT * FROM ais_info WHERE vsslNm LIKE ?`
  - `load_by_flag(flag)` → `SELECT * FROM ais_info WHERE flag = ?`
  - `filter_by_ship_type(type)` → `SELECT * FROM ais_info WHERE vsslTp = ?`

---

## 📝 **요약**

### 데이터베이스 사용 현황
| DB | 테이블 | 용도 | 레코드 예시 |
|----|--------|------|------------|
| **SQLite** | `ais_info` | AIS 원본 데이터 (선박 정보) | ~898 rows |
| **MySQL** | `data_inspection_results` | 품질 검사 결과 | ~5,388 rows |
| **MySQL** | `data_inspection_info` | 검사 메타데이터 | ~6 inspections |
| **MySQL** | `data_inspection_summary` | 검사 요약 정보 | ~6 summaries |
| **MySQL** | `api_response_data` | API 응답 원본 데이터 | varies |

### 주요 특징
1. **이중 데이터베이스 구조**: SQLite (원본) + MySQL (품질)
2. **실시간 품질 모니터링**: MQTT를 통한 자동 품질 검사
3. **기간별 통계**: 일별/주별/월별 검사 히스토리
4. **다차원 분석**: 필드별, 검사타입별, 심각도별 분석
5. **완전성 및 유효성 검사**: 데이터 품질 두 가지 차원 평가

---

**생성일**: 2025-10-16  
**버전**: 1.0  
**작성자**: AI Assistant

