"""TC (Terminal Container) routes"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

# Import models from centralized schemas
from models import (
    TCSummaryData,
    TCWorkHistoryData,
    QualitySummaryData
)

# Import utilities
from utils import (
    get_current_timestamp,
    calculate_pass_rate,
    create_response_data,
    create_error_response,
    validate_period,
    get_sql_date_condition,
    get_sql_group_by
)

# Import database utilities
from config import execute_query, execute_query_one

# Import cache system
from services.cache.cache_decorator import cached
from services.cache.cache_keys import CacheNamespace, CacheEndpoint
from config.redis_config import redis_settings

router = APIRouter()

@router.get("/tc-quality-summary")
@cached(
    namespace=CacheNamespace.TC,
    endpoint=CacheEndpoint.QUALITY_SUMMARY,
    ttl=redis_settings.CACHE_TTL_LONG  # 1시간 캐싱
)
async def get_tc_quality_summary():
    """TC 품질 요약 데이터 (캐싱 적용: 1시간)"""
    # 디버그: 함수 진입 확인
    import logging
    logger = logging.getLogger(__name__)
    logger.info("🚨 [TC] get_tc_quality_summary 함수 직접 실행됨!")
    
    try:
        # 전체 품질 통계
        overall_stats = execute_query_one("""
            SELECT 
                COUNT(DISTINCT inspection_id) as total_inspections,
                COUNT(*) as total_checks,
                SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
                MAX(created_at) as last_inspection
            FROM data_inspection_results 
            WHERE inspection_id LIKE '%%tc_work%%'
        """)
        
        if overall_stats:
            total_inspections, total_checks, pass_count, fail_count, last_inspection = overall_stats
            pass_rate = calculate_pass_rate(pass_count, total_checks)
        else:
            total_inspections = total_checks = pass_count = fail_count = pass_rate = 0
            last_inspection = None
        
        # 완전성 검사 통계
        completeness_stats = execute_query_one("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count
            FROM data_inspection_results 
            WHERE inspection_id LIKE '%%tc_work%%' AND check_type = 'completeness'
        """)
        
        completeness_rate = 0.0
        completeness_total = completeness_passed = 0
        if completeness_stats and completeness_stats[0] > 0:
            completeness_total = completeness_stats[0]
            completeness_passed = completeness_stats[1]
            completeness_rate = calculate_pass_rate(completeness_passed, completeness_total)
        
        # 유효성 검사 통계
        validity_stats = execute_query_one("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count
            FROM data_inspection_results 
            WHERE inspection_id LIKE '%%tc_work%%' AND check_type = 'validity'
        """)
        
        validity_rate = 0.0
        validity_total = validity_passed = 0
        if validity_stats and validity_stats[0] > 0:
            validity_total = validity_stats[0]
            validity_passed = validity_stats[1]
            validity_rate = calculate_pass_rate(validity_passed, validity_total)
        
        quality_data = {
            "total_inspections": int(total_inspections),
            "total_checks": int(total_checks),
            "pass_count": int(pass_count),
            "fail_count": int(fail_count),
            "pass_rate": float(pass_rate),
            "last_inspection_date": last_inspection.strftime('%Y-%m-%d') if last_inspection else get_current_timestamp(),
            "completeness": {
                "fields_checked": int(completeness_total),
                "pass_count": int(completeness_passed),
                "fail_count": int(completeness_total - completeness_passed) if completeness_total else 0,
                "pass_rate": float(completeness_rate)
            },
            "validity": {
                "fields_checked": int(validity_total),
                "pass_count": int(validity_passed),
                "fail_count": int(validity_total - validity_passed) if validity_total else 0,
                "pass_rate": float(validity_rate)
            }
        }
        
        return create_response_data([quality_data])
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"TC 품질 요약 조회 실패: {str(e)}"
        )

@router.get("/tc-summary", response_model=TCSummaryData)
async def get_tc_summary():
    """TC 작업 요약 정보"""
    try:
        # TC 작업 더미 데이터
        summary_data = TCSummaryData(
            total_work=1250,
            total_terminals=8,
            total_ships=45,
            total_containers=3200,
            work_days=30,
            recent_work=125,
            active_terminals=6,
            active_ships=12,
            work_types=[
                {"type": "Loading", "count": 650},
                {"type": "Unloading", "count": 400},
                {"type": "Shifting", "count": 200}
            ],
            terminals=[
                {"name": "Terminal A", "work_count": 320},
                {"name": "Terminal B", "work_count": 280},
                {"name": "Terminal C", "work_count": 250}
            ],
            last_inspection_date=get_current_timestamp()
        )
        
        return summary_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"TC 요약 조회 실패: {str(e)}"
        )

@router.get("/tc-work-history")
async def get_tc_work_history():
    """TC 작업 히스토리"""
    try:
        # 최근 30일간 TC 작업 히스토리 더미 데이터
        history_data = []
        base_date = datetime.now()
        
        for i in range(30):
            work_date = base_date - timedelta(days=i)
            history_data.append({
                "work_date": work_date.strftime("%Y-%m-%d"),
                "total_work": 40 + (i % 10),
                "terminals": 3 + (i % 3),
                "ships": 5 + (i % 5),
                "containers": 120 + (i % 30)
            })
        
        return create_response_data(history_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"TC 작업 히스토리 조회 실패: {str(e)}"
        )

@router.get("/tc-quality-status")
async def get_tc_quality_status():
    """TC 데이터 품질 상태"""
    try:
        # TC 품질 상태 더미 데이터
        quality_data = {
            "overall_status": "healthy",
            "alerts": [],
            "quality_metrics": {
                "overall_rate": 90.0,
                "total_inspections": 25,
                "total_checks": 800,
                "pass_count": 720,
                "fail_count": 80,
                "last_inspection_date": get_current_timestamp()
            },
            "work_quality": {
                "loading_accuracy": 95.5,
                "unloading_accuracy": 92.3,
                "shifting_accuracy": 88.7
            },
            "terminal_performance": [
                {"terminal": "Terminal A", "efficiency": 94.2},
                {"terminal": "Terminal B", "efficiency": 91.8},
                {"terminal": "Terminal C", "efficiency": 89.5}
            ]
        }
        
        return create_response_data([quality_data])
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"TC 품질 상태 조회 실패: {str(e)}"
        )

@router.get("/tc-field-analysis")
async def get_tc_field_analysis():
    """TC 필드별 상세 분석 데이터"""
    try:
        import json
        import re
        
        # details JSON에서 필드별 통계를 추출 (가장 최근 검사 결과만)
        all_results = execute_query("""
            SELECT 
                check_type,
                status,
                details,
                affected_rows
            FROM data_inspection_results 
            WHERE inspection_id LIKE '%%tc_work%%' 
            AND details IS NOT NULL AND details != ''
            AND created_at = (
                SELECT MAX(created_at) 
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%%tc_work%%'
            )
            ORDER BY check_type
        """)
        
        # 필드별로 데이터 집계
        field_data = {}
        
        for row in all_results:
            check_type = row[0]
            status = row[1]
            details_str = row[2]
            affected_rows = row[3] or 0
            
            try:
                details = json.loads(details_str)
                message = details.get('message', '')
                
                # 메시지에서 필드명 추출: [필드명] 형식
                match = re.search(r'\[([^\]]+)\]', message)
                if not match:
                    continue
                    
                field_name = match.group(1)
                total = details.get('total', 0)
                check_count = int(details.get('check', 0))
                etc_count = int(details.get('etc', 0))
                
                # 필드별 키 생성
                key = f"{field_name}_{check_type}"
                
                if key not in field_data:
                    field_data[key] = {
                        'field_name': field_name,
                        'check_type': check_type,
                        'total': total,
                        'pass_count': 0,
                        'fail_count': 0,
                        'error_sum': 0,
                        'max_affected_rows': 0,  # 최대 affected_rows 추적
                        'last_message': message  # 원본 메시지 저장
                    }
                else:
                    # 마지막 메시지 업데이트 (최신 것으로)
                    field_data[key]['last_message'] = message
                
                # 상태별 집계
                if status == 'PASS':
                    field_data[key]['pass_count'] += 1
                else:
                    field_data[key]['fail_count'] += 1
                    # 중복 집계 방지: 최대값만 저장
                    field_data[key]['max_affected_rows'] = max(field_data[key]['max_affected_rows'], affected_rows)
                    field_data[key]['error_sum'] = field_data[key]['max_affected_rows']
                    
            except (json.JSONDecodeError, ValueError) as e:
                continue
        
        # 리스트로 변환
        field_stats = []
        for key, data in field_data.items():
            total_checks = data['pass_count'] + data['fail_count']
            pass_rate = (data['pass_count'] * 100.0 / total_checks) if total_checks > 0 else 0
            
            # 마지막 메시지 저장 (가장 최근 것)
            last_message = data.get('last_message', '')
            
            field_stats.append((
                data['field_name'],
                data['check_type'],
                data['total'],  # 실제 검사한 레코드 수
                data['pass_count'],  # PASS 횟수
                data['fail_count'],  # FAIL 횟수
                pass_rate,
                data['error_sum'],  # 오류/빈값의 합계
                last_message  # 원본 메시지
            ))
        
        # 심각도별 통계
        severity_stats = execute_query("""
            SELECT 
                severity,
                COUNT(*) as count,
                check_type
            FROM data_inspection_results 
            WHERE inspection_id LIKE '%%tc_work%%' AND severity IS NOT NULL
            GROUP BY severity, check_type
            ORDER BY count DESC
        """)
        
        analysis_data = {
            "field_statistics": [
                {
                    "field_name": row[0],
                    "check_type": row[1],
                    "total_checks": row[2],  # 실제 검사한 레코드 수
                    "pass_count": row[3],  # PASS 횟수
                    "fail_count": row[4],  # FAIL 횟수
                    "pass_rate": float(row[5]),
                    "affected_rows": row[6],  # 오류/빈값 합계
                    "original_message": row[7] if len(row) > 7 else ""  # 원본 메시지
                } for row in field_stats
            ],
            "severity_distribution": [
                {
                    "severity": row[0],
                    "count": row[1],
                    "check_type": row[2]
                } for row in severity_stats
            ]
        }
        
        return create_response_data([analysis_data])
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"TC 필드별 분석 실패: {str(e)}"
        )

@router.get("/tc-inspection-history")
async def get_tc_inspection_history(
    period: str = Query(default="daily", description="기간 타입: daily, weekly, monthly, custom"),
    start_date: Optional[str] = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="종료 날짜 (YYYY-MM-DD)")
):
    """TC 검사 히스토리 데이터 (기간별 필터링 지원)"""
    try:
        if not validate_period(period):
            raise HTTPException(
                status_code=400, 
                detail="period는 'daily', 'weekly', 'monthly', 'custom' 중 하나여야 합니다."
            )
        
        # 날짜 조건 및 그룹화 설정
        date_condition, date_params = get_sql_date_condition(period, start_date, end_date)
        group_by, date_format = get_sql_group_by(period)
        
        # 검사 히스토리 쿼리
        query = f"""
            SELECT 
            {date_format} as period_label,
            {group_by} as period_key,
            COUNT(*) as total_checks,
            SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
            SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
            ROUND(SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pass_rate,
            SUM(CASE WHEN check_type = 'completeness' AND status = 'PASS' THEN 1 ELSE 0 END) as completeness_pass,
            SUM(CASE WHEN check_type = 'completeness' THEN 1 ELSE 0 END) as completeness_total,
            SUM(CASE WHEN check_type = 'validity' AND status = 'PASS' THEN 1 ELSE 0 END) as validity_pass,
            SUM(CASE WHEN check_type = 'validity' THEN 1 ELSE 0 END) as validity_total
            FROM data_inspection_results 
            WHERE inspection_id LIKE '%%tc_work%%'
            {date_condition}
            GROUP BY {group_by}
            ORDER BY {group_by} ASC
            LIMIT 50
        """
        
        results = execute_query(query, date_params)
            
        history_data = []
        for row in results:
            completeness_rate = calculate_pass_rate(row[6], row[7]) if row[7] > 0 else 0.0
            validity_rate = calculate_pass_rate(row[8], row[9]) if row[9] > 0 else 0.0
                
            history_data.append({
                "date": str(row[0]),
                "score": float(row[5]),
                "totalChecks": row[2],
                "passedChecks": row[3],
                "failedChecks": row[4],
                "completenessRate": completeness_rate,
                "validityRate": validity_rate
                })
        
        return history_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"TC 검사 히스토리 조회 실패: {str(e)}"
        )