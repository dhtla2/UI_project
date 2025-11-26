# 업데이트된 동기화 서비스 사용법

## 🎯 개요

API 응답 결과(`api_structure_results_20250825_145133.json`)를 기반으로 업데이트된 DB 구조에 맞게 동기화 서비스가 최적화되었습니다.

## 🔄 주요 변경사항

### 1. **새로운 테이블 지원 추가**
- **tc_work_info**: TC 작업 정보 (188,880건 예상)
- **qc_work_info**: QC 작업 정보 (90,793건 예상)
- **yt_work_info**: YT 작업 정보 (85,872건 예상)
- **berth_schedule**: 선석 계획

### 2. **중복 처리 로직 최적화**
- 각 테이블별 맞춤형 중복 처리 로직
- `ON DUPLICATE KEY UPDATE` 구문으로 효율적인 데이터 업데이트
- `updated_at` 타임스탬프 자동 업데이트

### 3. **테이블 목록 중앙화**
- 25개 테이블 목록을 `DBSyncManager.all_tables`에 중앙 관리
- 테이블 추가/제거 시 한 곳에서만 수정

## 🚀 사용 방법

### 1. **테스트 실행 (권장)**
```bash
cd UI_project/db

# 업데이트된 동기화 서비스 테스트
python test_updated_sync_service.py
```

### 2. **동기화 서비스 실행**
```bash
cd UI_project/db

# 전체 동기화
python run_sync_service.py --manual-sync --sync-type full

# 특정 엔드포인트만 동기화
python run_sync_service.py --endpoint tc_work_info

# 우선순위별 동기화
python run_sync_service.py --priority high

# 카테고리별 동기화
python run_sync_service.py --category work_info
```

### 3. **스케줄러 사용**
```bash
# 스케줄러 시작
python run_sync_service.py --start-scheduler

# 스케줄러 중지
python run_sync_service.py --stop-scheduler

# 스케줄러 상태 확인
python run_sync_service.py --status
```

## 📊 지원하는 엔드포인트

### **작업 정보 (3개)**
| 엔드포인트 | 테이블명 | 예상 레코드 수 | 설명 |
|------------|----------|----------------|------|
| `tc_work_info` | `tc_work_info` | 188,880건 | TC 작업 정보 |
| `qc_work_info` | `qc_work_info` | 90,793건 | QC 작업 정보 |
| `yt_work_info` | `yt_work_info` | 85,872건 | YT 작업 정보 |

### **선박 정보 (8개)**
| 엔드포인트 | 테이블명 | 예상 레코드 수 | 설명 |
|------------|----------|----------------|------|
| `ais_info` | `ais_info` | 898건 | AIS 정보 |
| `vssl_entr_report` | `vssl_entr_report` | 1건 | 선박 입항신고정보 |
| `vssl_dprt_report` | `vssl_dprt_report` | 1건 | 선박 출항신고정보 |
| `vssl_history` | `vssl_history` | 2건 | 관제정보 |
| `vssl_pass_report` | `vssl_pass_report` | 1건 | 외항통과선박신청정보 |
| `vssl_sanction_info` | `vssl_sanction_info` | 2건 | 제재대상선박 정보 |
| `vssl_sec_isps_info` | `vssl_sec_isps_info` | 1건 | 선박보안인증서 통보 |
| `vssl_sec_port_info` | `vssl_sec_port_info` | 10건 | 선박보안인증서 통보 경유지 정보 |

### **컨테이너 정보 (2개)**
| 엔드포인트 | 테이블명 | 예상 레코드 수 | 설명 |
|------------|----------|----------------|------|
| `cntr_load_unload_info` | `cntr_load_unload_info` | 1,012건 | 컨테이너 양적하정보 |
| `cntr_report_detail` | `cntr_report_detail` | 1건 | 컨테이너 신고상세정보 |

### **화물 및 위험물 (3개)**
| 엔드포인트 | 테이블명 | 예상 레코드 수 | 설명 |
|------------|----------|----------------|------|
| `cargo_imp_exp_report` | `cargo_imp_exp_report` | 0건 | 화물반출입신고정보 |
| `cargo_item_code` | `cargo_item_code` | 1건 | 화물품목코드 |
| `dg_imp_report` | `dg_imp_report` | 1건 | 위험물반입신고서 |

### **항만시설 (2개)**
| 엔드포인트 | 테이블명 | 예상 레코드 수 | 설명 |
|------------|----------|----------------|------|
| `fac_use_statement` | `fac_use_statement` | 1건 | 항만시설사용 신청/결과정보 |
| `fac_use_stmt_bill` | `fac_use_stmt_bill` | 1건 | 항만시설사용신고정보-화물료 |

### **기타 정보 (7개)**
| 엔드포인트 | 테이블명 | 예상 레코드 수 | 설명 |
|------------|----------|----------------|------|
| `berth_schedule` | `berth_schedule` | 0건 | 선석 계획 |
| `dg_manifest` | `dg_manifest` | 0건 | 위험물 적하알림표 |
| `load_unload_from_to_info` | `load_unload_from_to_info` | 2건 | 선박양적하 시작종료정보 |
| `country_code` | `country_code` | 1건 | 국가코드 |
| `vssl_entr_intn_code` | `vssl_entr_intn_code` | 1건 | 입항목적코드 |
| `pa_code` | `pa_code` | 1건 | 항구청코드 |
| `port_code` | `port_code` | 1건 | 항구코드 |

## 🔧 중복 처리 로직

### **TC 작업정보**
```sql
-- 중복 키: tmnlId + shpCd + callYr + serNo + tcNo
ON DUPLICATE KEY UPDATE
    cntrNo = VALUES(cntrNo),
    tmnlNm = VALUES(tmnlNm),
    shpNm = VALUES(shpNm),
    -- ... 기타 필드들
    updated_at = CURRENT_TIMESTAMP
```

### **QC 작업정보**
```sql
-- 중복 키: tmnlId + shpCd + callYr + serNo + qcNo
ON DUPLICATE KEY UPDATE
    cntrNo = VALUES(cntrNo),
    ytNo = VALUES(ytNo),
    -- ... 기타 필드들
    updated_at = CURRENT_TIMESTAMP
```

### **AIS 정보**
```sql
-- 중복 키: mmsiNo + imoNo + callLetter
ON DUPLICATE KEY UPDATE
    vsslNm = VALUES(vsslNm),
    vsslTp = VALUES(vsslTp),
    -- ... 기타 필드들
    updated_at = CURRENT_TIMESTAMP
```

## 📈 성능 최적화

### 1. **인덱스 활용**
- 각 테이블에 적절한 인덱스 설정
- 중복 체크를 위한 복합 인덱스 최적화

### 2. **배치 처리**
- `executemany()`를 사용한 대량 데이터 삽입
- 트랜잭션 단위로 커밋하여 성능 향상

### 3. **중복 처리 최적화**
- `ON DUPLICATE KEY UPDATE`로 INSERT + UPDATE 통합
- 불필요한 SELECT 쿼리 제거

## 🧪 테스트 및 검증

### 1. **테스트 스크립트 실행**
```bash
python test_updated_sync_service.py
```

### 2. **테스트 항목**
- ✅ DB 연결 테스트
- ✅ 테이블 구조 테스트
- ✅ 엔드포인트 매핑 테스트
- ✅ 샘플 데이터 삽입 테스트
- ✅ 동기화 상태 조회 테스트

### 3. **검증 포인트**
- 모든 25개 테이블이 정상적으로 생성되었는지 확인
- 컬럼 구조가 API 응답과 일치하는지 확인
- 중복 처리 로직이 정상 작동하는지 확인

## ⚠️ 주의사항

### 1. **실행 전 확인사항**
- MySQL 서버가 실행 중인지 확인
- `port_database` 데이터베이스가 존재하는지 확인
- 업데이트된 DB 스키마가 적용되었는지 확인

### 2. **데이터 백업**
- 기존 데이터가 있다면 백업 후 실행
- `update_database_structure.py`로 자동 백업 가능

### 3. **리소스 관리**
- 대용량 데이터 동기화 시 메모리 사용량 모니터링
- 디스크 공간 충분히 확보

## 🔍 문제 해결

### 1. **테이블이 존재하지 않는 경우**
```bash
# DB 구조 업데이트 실행
python update_database_structure.py
```

### 2. **중복 처리 오류**
```sql
-- 테이블 구조 확인
DESCRIBE {테이블명};

-- 인덱스 확인
SHOW INDEX FROM {테이블명};
```

### 3. **성능 문제**
```bash
# 동기화 상태 확인
python run_sync_service.py --status

# 로그 파일 확인
tail -f sync_service_YYYYMMDD.log
```

## 📞 지원

문제가 발생하거나 추가 지원이 필요한 경우:
1. 테스트 스크립트 실행 결과 확인
2. 로그 파일에서 오류 메시지 확인
3. MySQL 에러 로그 확인

## 🎉 결론

업데이트된 동기화 서비스는 **25개 테이블**을 지원하며, **API 응답과 100% 일치하는 DB 구조**로 최적화되었습니다. 

특히 **TC/QC/YT 작업정보**와 같은 대용량 데이터를 효율적으로 처리할 수 있도록 중복 처리 로직이 개선되었습니다.

이제 `run_sync_service.py`를 사용하여 모든 API 엔드포인트에서 안전하고 효율적인 데이터 동기화를 수행할 수 있습니다! 🚀
