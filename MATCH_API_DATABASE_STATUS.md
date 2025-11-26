# Match API 데이터베이스 상태 확인 결과

## 📋 **확인 일시**: 2025-10-16

---

## ❌ **결과: 원본 데이터 테이블 없음**

### 확인된 사실

**1. vssl_Tos_VsslNo 테이블: 존재하지 않음** ❌
- MySQL `port_database`에 테이블 없음
- CSV 파일도 없음

**2. vssl_Port_VsslNo 테이블: 존재하지 않음** ❌
- MySQL `port_database`에 테이블 없음
- CSV 파일도 없음

---

## 🗄️ **현재 존재하는 vssl 관련 테이블**

```
✅ vssl_dprt_report        (선박 출항 보고)
✅ vssl_entr_intn_code     (입항 목적 코드)
✅ vssl_entr_report        (선박 입항 보고)
✅ vssl_history            (선박 이력) - 2개 행
✅ vssl_pass_report        (선박 통과 보고)
✅ vssl_sanction_info      (제재 대상 선박 정보)
✅ vssl_sec_isps_info      (선박 보안 ISPS 정보)
✅ vssl_sec_port_info      (선박 보안 항구 정보)
```

---

## 🔍 **Match API는 어떻게 작동하는가?**

### API 호출 흐름

```
1. 사용자/시스템이 Match API 호출
   ↓
2. API가 실시간으로 TOS ↔ PMIS 매칭 수행
   ↓
3. 매칭 결과 1개 반환 (JSON)
   ↓
4. 품질 검사 수행 (MQTT)
   ↓
5. 검사 결과만 DB에 저장 (data_inspection_results)
   ↓
6. 원본 매칭 데이터는 저장 안 됨 ❌
```

### 실제 동작 확인

**테스트 결과** (2025-10-16 10:37):
```json
vssl_Tos_VsslNo API 응답:
{
  "prtAtCd": "020",
  "callYrPmis": "2022",
  "callSignPmis": "5LDA9",
  "callSeqPmis": "001",
  "tmnlCd": "BPTG",
  "callYrTos": "2022",
  "vsslCdTos": "SBVG",
  "callSeqTos": "001"
}
```

✅ **API는 정상 동작**  
✅ **품질 검사 완료** (8개 필드 모두 PASS)  
❌ **원본 데이터는 DB에 저장 안 됨**

---

## 📊 **저장되는 데이터 vs 저장 안 되는 데이터**

### ✅ 저장되는 데이터

| 테이블 | 내용 | 위치 |
|--------|------|------|
| `data_inspection_results` | 품질 검사 결과 | MySQL |
| `data_inspection_info` | 검사 메타데이터 | MySQL |
| `data_inspection_summary` | 검사 요약 | MySQL |
| `api_response_data` | API 응답 메타데이터 (빈 데이터) | MySQL |

### ❌ 저장 안 되는 데이터

| API | 반환 데이터 | 저장 여부 |
|-----|-----------|----------|
| `vssl_Tos_VsslNo` | TOS→PMIS 매칭 정보 (8개 필드) | ❌ 저장 안 됨 |
| `vssl_Port_VsslNo` | PMIS→TOS 매칭 정보 (8개 필드) | ❌ 저장 안 됨 |

---

## 💡 **왜 저장하지 않는가?**

### 가능한 이유:

1. **실시간 조회 서비스**
   - 매칭 정보는 실시간으로 조회하는 용도
   - 이력 관리가 필요 없음

2. **소량 데이터**
   - 호출당 1개의 매칭 결과만 반환
   - 대량 데이터가 아니므로 저장 불필요

3. **휘발성 데이터**
   - 매칭 결과는 파라미터에 따라 달라짐
   - 저장하면 중복 데이터 발생 가능

4. **기존 설계**
   - 다른 vssl 테이블들은 API에서 가져온 대량 데이터 저장
   - Match API는 조회만 수행하도록 설계됨

---

## 🔧 **해결 방법**

### 옵션 1: 테이블 생성 (권장하지 않음)

**테이블 생성 SQL:**
```sql
-- vssl_Tos_VsslNo 테이블
CREATE TABLE vssl_Tos_VsslNo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(10),
    callYrPmis VARCHAR(4),
    callSignPmis VARCHAR(20),
    callSeqPmis VARCHAR(10),
    tmnlCd VARCHAR(10),
    callYrTos VARCHAR(4),
    vsslCdTos VARCHAR(20),
    callSeqTos VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_pmis (callYrPmis, callSignPmis, callSeqPmis),
    INDEX idx_tos (callYrTos, vsslCdTos, callSeqTos),
    INDEX idx_created (created_at)
);

-- vssl_Port_VsslNo 테이블
CREATE TABLE vssl_Port_VsslNo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(10),
    callYrPmis VARCHAR(4),
    callSignPmis VARCHAR(20),
    callSeqPmis VARCHAR(10),
    tmnlCd VARCHAR(10),
    callYrTos VARCHAR(4),
    vsslCdTos VARCHAR(20),
    callSeqTos VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_pmis (callYrPmis, callSignPmis, callSeqPmis),
    INDEX idx_tos (callYrTos, vsslCdTos, callSeqTos),
    INDEX idx_created (created_at)
);
```

**문제점:**
- 중복 데이터 발생 가능
- 동일 파라미터로 여러 번 호출 시 동일 데이터 반복 저장
- 저장 시점 관리 필요

### 옵션 2: 현재 상태 유지 (권장) ✅

**이유:**
- API는 정상 작동 중
- 품질 검사는 수행됨
- 매칭 서비스는 실시간 조회가 목적
- 이력 관리가 불필요

### 옵션 3: 매칭 이력 테이블 생성

**필요시 생성할 수 있는 이력 테이블:**
```sql
CREATE TABLE vssl_matching_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    api_type ENUM('TOS_TO_PMIS', 'PMIS_TO_TOS') NOT NULL,
    request_params JSON NOT NULL,
    response_data JSON NOT NULL,
    match_success BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_api_type (api_type),
    INDEX idx_created (created_at)
);
```

**장점:**
- 매칭 이력 추적 가능
- 통계 분석 가능
- 중복 최소화 (JSON 저장)

---

## 📈 **현재 데이터 상태**

### MySQL: data_inspection_results

```sql
-- vssl_Tos_VsslNo 검사 결과
inspection_id: vssl_tos_vsslno_inspection_1760578679_319e09
- 검사일시: 2025-10-16 10:37:59
- 총 검사: 8개
- 통과: 8개 (100%)
- 실패: 0개
- 품질 점수: 100점

-- vssl_Port_VsslNo 검사 결과
inspection_id: vssl_port_vsslno_inspection_1760578671_7a26ce
- 검사일시: 2025-10-16 10:37:51
- 총 검사: 8개
- 통과: 8개 (100%)
- 실패: 0개
- 품질 점수: 100점
```

### 검사된 필드 (8개)

✅ prtAtCd (항만청 코드)  
✅ callYrPmis (PMIS 호출년도)  
✅ callSignPmis (PMIS 호출부호)  
✅ callSeqPmis (PMIS 호출순번)  
✅ tmnlCd (터미널 코드)  
✅ callYrTos (TOS 호출년도)  
✅ vsslCdTos (TOS 선박코드)  
✅ callSeqTos (TOS 호출순번)  

---

## 🎯 **결론**

### 현재 상황
1. ✅ **Match API는 정상 작동**
2. ✅ **품질 검사는 수행되고 저장됨**
3. ❌ **원본 매칭 데이터는 저장 안 됨**
4. ✅ **이는 의도된 동작으로 보임**

### 권장사항

**🔵 현재 상태 유지 (권장)**
- Match API는 실시간 조회 서비스
- 품질 검사는 정상 수행 중
- 추가 저장 불필요

**🔴 테이블 생성 (필요시)**
- 매칭 이력이 필요한 경우에만 생성
- `vssl_matching_history` 형태로 JSON 저장 권장

---

## 📝 **비교: 다른 API와의 차이**

| API 타입 | 원본 데이터 저장 | 품질 검사 | 예시 |
|----------|----------------|----------|------|
| **대량 데이터 API** | ✅ 저장 (테이블) | ✅ 수행 | AIS, TC, QC, TOS |
| **매칭 API** | ❌ 미저장 | ✅ 수행 | vssl_Tos_VsslNo, vssl_Port_VsslNo |
| **코드 API** | ✅ 저장 (소량) | ✅ 수행 | country_code, port_code |

---

**문서 작성일**: 2025-10-16  
**확인자**: AI Assistant  
**상태**: 정상 (원본 데이터 미저장은 의도된 동작)

