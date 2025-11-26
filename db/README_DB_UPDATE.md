# DB 구조 업데이트 가이드

## 📋 개요

API 응답 결과(`api_structure_results_20250825_145133.json`)를 기반으로 데이터베이스 테이블 구조를 업데이트합니다.

## 🔍 주요 변경사항

### 1. 새로운 테이블 추가
- **tc_work_info**: TC 작업 정보 (188,880건 예상)
- **qc_work_info**: QC 작업 정보 (90,793건 예상)  
- **yt_work_info**: YT 작업 정보 (85,872건 예상)
- **berth_schedule**: 선석 계획

### 2. 기존 테이블 구조 업데이트
- **ais_info**: AIS 정보 (898건)
- **cntr_load_unload_info**: 컨테이너 양적하정보 (1,012건)
- **cntr_report_detail**: 컨테이너 신고상세정보 (1건)
- **vssl_entr_report**: 선박 입항신고정보 (1건)
- **vssl_dprt_report**: 선박 출항신고정보 (1건)
- **vssl_history**: 관제정보 (2건)
- **vssl_pass_report**: 외항통과선박신청정보 (1건)
- **cargo_item_code**: 화물품목코드 (1건)
- **dg_imp_report**: 위험물반입신고서 (1건)
- **fac_use_statement**: 항만시설사용 신청/결과정보 (1건)
- **fac_use_stmt_bill**: 항만시설사용신고정보-화물료 (1건)
- **vssl_sec_isps_info**: 선박보안인증서 통보 (1건)
- **vssl_sec_port_info**: 선박보안인증서 통보 경유지 정보 (10건)
- **load_unload_from_to_info**: 선박양적하 시작종료정보 (2건)
- **vssl_sanction_info**: 제재대상선박 정보 (2건)
- **country_code**: 국가코드 (1건)
- **vssl_entr_intn_code**: 입항목적코드 (1건)
- **pa_code**: 항구청코드 (1건)
- **port_code**: 항구코드 (1건)

### 3. 데이터가 없는 테이블
- **cargo_imp_exp_report**: 화물반출입신고정보 (0건)
- **dg_manifest**: 위험물 적하알림표 (0건)
- **berth_schedule**: 선석 계획 (0건)

## 🚀 실행 방법

### 1. 자동 실행 (권장)
```bash
cd UI_project/db

# Python 스크립트로 자동 실행
python update_database_structure.py
```

### 2. 수동 실행
```bash
cd UI_project/db

# MySQL에 직접 연결하여 SQL 실행
mysql -h localhost -P 3307 -u root -p port_database < updated_database_schema.sql
```

## 📁 생성되는 파일들

### 1. SQL 스키마 파일
- **`updated_database_schema.sql`**: 업데이트된 DB 스키마

### 2. 실행 스크립트
- **`update_database_structure.py`**: 자동 실행 Python 스크립트

### 3. 로그 파일
- **`db_update_YYYYMMDD_HHMMSS.log`**: 실행 로그 (자동 생성)

## 🔒 안전장치

### 1. 자동 백업
- 기존 테이블을 `{테이블명}_backup_{타임스탬프}` 형식으로 자동 백업
- 데이터 손실 방지

### 2. 트랜잭션 처리
- 각 SQL 문을 개별적으로 실행하여 오류 발생 시 부분 롤백 가능
- 전체 프로세스 실패 시에도 기존 데이터 보존

### 3. 상세 로깅
- 모든 작업 과정을 로그 파일에 기록
- 오류 발생 시 원인 파악 가능

## 📊 예상 결과

### 테이블 수
- **이전**: 20개 테이블
- **이후**: 25개 테이블 (+5개)

### 총 레코드 수
- **이전**: 기존 데이터 유지
- **이후**: 약 365,000건 이상 (새로운 테이블 포함)

### 주요 데이터 소스
- **TC 작업 정보**: 188,880건 (가장 많은 데이터)
- **QC 작업 정보**: 90,793건
- **YT 작업 정보**: 85,872건
- **AIS 정보**: 898건

## ⚠️ 주의사항

### 1. 실행 전 확인사항
- MySQL 서버가 실행 중인지 확인
- `port_database` 데이터베이스가 존재하는지 확인
- 충분한 디스크 공간 확보 (백업 테이블 생성)

### 2. 실행 중 주의사항
- 다른 프로세스에서 DB에 접근하지 않도록 주의
- 네트워크 연결이 안정적인지 확인

### 3. 실행 후 확인사항
- 로그 파일에서 오류 메시지 확인
- 테이블 생성 결과 확인
- 백업 테이블 정상 생성 확인

## 🛠️ 문제 해결

### 1. 연결 오류
```bash
# MySQL 서비스 상태 확인
sudo systemctl status mysql

# 포트 확인
netstat -tlnp | grep 3307
```

### 2. 권한 오류
```sql
-- MySQL에서 권한 확인
SHOW GRANTS FOR 'root'@'localhost';

-- 필요시 권한 부여
GRANT ALL PRIVILEGES ON port_database.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

### 3. 디스크 공간 부족
```bash
# 디스크 사용량 확인
df -h

# MySQL 데이터 디렉토리 확인
mysql -e "SHOW VARIABLES LIKE 'datadir';"
```

## 📞 지원

문제가 발생하거나 추가 지원이 필요한 경우:
1. 로그 파일 확인
2. MySQL 에러 로그 확인
3. 시스템 리소스 상태 확인

## 🔄 롤백 방법

문제 발생 시 이전 상태로 복원:
```sql
-- 백업 테이블에서 원본 테이블로 복원
RENAME TABLE {테이블명} TO {테이블명}_current;
RENAME TABLE {테이블명}_backup_{타임스탬프} TO {테이블명};

-- 필요시 현재 테이블 삭제
DROP TABLE {테이블명}_current;
```
