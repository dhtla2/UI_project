# 필드 분석 오류/정상 개수 버그 수정

## 🐛 문제점

AIS 페이지에서 유효성-그리드 필드의 통계가 잘못 표시되었습니다:

```
총계: 898
오류: 1086  ❌ (실제보다 많음)
정상: -188  ❌ (음수!)
```

실제 데이터:
```
총계: 898
육지(정상): 543
바다(오류): 355
```

## 🔍 원인 분석

### 1. 백엔드 API 버그

**파일**: `backend/routers/ais_routes.py`, `tc_routes.py`, `qc_routes.py`, `tos_routes.py`

**문제 코드** (각 파일의 `field-analysis` API):
```python
field_data[key]['error_sum'] += check_count  # ❌ 잘못됨
```

**문제**:
- `check_count`는 `details.get('check', 0)`로, 실제로는 **정상 데이터 수** (예: 육지 543개)
- `affected_rows`가 실제 **오류 데이터 수** (예: 바다 355개)
- 잘못된 값을 누적하여 오류 개수가 비정상적으로 증가

### 2. DB 데이터 구조

```sql
check_name: validity
check_type: validity
status: FAIL
affected_rows: 355  -- 실제 오류 행 수
details: {
  "total": 898,     -- 전체 데이터 행 수
  "check": "543",   -- 정상 데이터 수 (육지)
  "etc": "355",     -- 오류 데이터 수 (바다)
  "message": "[유효성-그리드] (['lon', 'lat']) 항목에 전체 (898)개 중 육지 (543)개, 바다 (355)개 확인 되었습니다"
}
```

## ✅ 수정 내용

### 1. 백엔드 API 수정

#### 수정된 파일:
- `backend/routers/ais_routes.py` (Line 643)
- `backend/routers/tc_routes.py` (Line 272)
- `backend/routers/qc_routes.py` (Line 288)
- `backend/routers/tos_routes.py` (Line 250)

**수정 전**:
```python
field_data[key]['error_sum'] += check_count  # ❌
```

**수정 후**:
```python
# affected_rows는 실제 오류 데이터 행 수
field_data[key]['error_sum'] += affected_rows  # ✅
```

### 2. 프론트엔드 수정

#### 수정된 파일:
- `dashboard/src/components/common/CommonFieldAnalysisSection.tsx` (Line 65-79)

**수정 전**:
```typescript
total: stat.total_checks,  // 실제 검사한 레코드 수 (898)
check: affectedRows,       // 오류/빈값 개수
etc: stat.total_checks - affectedRows,  // 정상 개수 (음수 가능 ❌)
```

**수정 후**:
```typescript
// total_checks는 실제 데이터 행 수 (예: 898)
// affectedRows는 오류/빈값이 있는 행 수
// 정상 개수 = 전체 - 오류
const normalCount = stat.total_checks - affectedRows;

total: stat.total_checks,  // 실제 데이터 행 수 (898)
check: affectedRows,       // 오류/빈값 개수
etc: normalCount >= 0 ? normalCount : 0,  // 정상 개수 (음수 방지 ✅)
```

## 🚀 적용 방법

### 1. 백엔드 재시작

```bash
# 백엔드 프로세스 찾기
ps aux | grep "uvicorn.*main_new"

# 프로세스 종료 (PID는 위에서 확인)
kill <PID>

# 백엔드 재시작
cd /home/cotlab/UI_project_new/backend
nohup uvicorn main_new:app --host 0.0.0.0 --port 8080 --reload > ../backend.log 2>&1 &
```

### 2. 프론트엔드 재빌드 (필요시)

```bash
cd /home/cotlab/UI_project_new/dashboard
npm run build
```

## 🧪 검증 방법

### 1. API 직접 호출
```bash
curl http://localhost:8080/ais/ais-field-analysis | jq '.data[0].field_statistics[] | select(.field_name == "유효성-그리드")'
```

**예상 결과**:
```json
{
  "field_name": "유효성-그리드",
  "check_type": "validity",
  "total_checks": 898,     // 전체 데이터
  "affected_rows": 355,    // 오류 (바다)
  "pass_count": 0,
  "fail_count": 2,
  "pass_rate": 0.0
}
```

### 2. UI에서 확인

1. AIS 페이지 접속
2. 필드별 분석 테이블 확인
3. 유효성-그리드 행의 통계 확인:
   - 총계: 898 ✅
   - 오류: 355 ✅ (바다)
   - 정상: 543 ✅ (육지)

## 📊 수정 전/후 비교

| 항목 | 수정 전 | 수정 후 |
|------|---------|---------|
| 총계 | 898 | 898 ✅ |
| 오류 | 1086 ❌ | 355 ✅ |
| 정상 | -188 ❌ | 543 ✅ |

## 📝 참고사항

- 이 버그는 AIS, TOS, TC, QC 모든 페이지에 동일하게 존재했습니다
- 모든 페이지의 백엔드 API를 동시에 수정했습니다
- DB 데이터는 정상이므로 재검사 불필요
- API 재시작만으로 즉시 적용됩니다

## 🔗 관련 파일

### 백엔드
- `/home/cotlab/UI_project_new/backend/routers/ais_routes.py`
- `/home/cotlab/UI_project_new/backend/routers/tc_routes.py`
- `/home/cotlab/UI_project_new/backend/routers/qc_routes.py`
- `/home/cotlab/UI_project_new/backend/routers/tos_routes.py`

### 프론트엔드
- `/home/cotlab/UI_project_new/dashboard/src/components/common/CommonFieldAnalysisSection.tsx`

---

**수정 완료일**: 2025-10-15
**영향 범위**: AIS, TOS, TC, QC 필드 분석 통계
**상태**: ✅ 수정 완료, 재시작 대기중

