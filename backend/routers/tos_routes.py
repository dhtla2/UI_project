"""TOS (Terminal Operating System) routes"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

# Import models from centralized schemas
from models import (
    TOSSummaryData,
    TOSWorkHistoryData,
    QualitySummaryData
)

# Import utilities
from utils import (
    get_current_timestamp,
    calculate_pass_rate,
    get_sql_date_condition,
    get_sql_group_by,
    validate_period,
    create_response_data,
    create_error_response
)

# Import database utilities
from config import execute_query, execute_query_one

# Import cache system
from services.cache.cache_decorator import cached
from services.cache.cache_keys import CacheNamespace, CacheEndpoint
from config.redis_config import redis_settings

router = APIRouter()

@router.get("/tos-quality-details")
async def get_tos_quality_details():
    """TOS 품질 상세 데이터"""
    try:
        # 최근 검사 결과
        recent_inspections = execute_query("""
            SELECT 
                inspection_id,
                check_type,
                check_name,
                status,
                message,
                created_at
            FROM data_inspection_results 
            WHERE inspection_id LIKE '%%berth%%'
            ORDER BY created_at DESC 
            LIMIT 50
        """)
        
        # 검사 타입별 통계
        check_type_stats = execute_query("""
            SELECT 
                check_type,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
            FROM data_inspection_results 
            WHERE inspection_id LIKE '%%berth%%'
            GROUP BY check_type
        """)
        
        # 실패 원인 분석
        failure_analysis = execute_query("""
            SELECT 
                check_name,
                message,
                COUNT(*) as failure_count
            FROM data_inspection_results 
            WHERE inspection_id LIKE '%%berth%%' AND status = 'FAIL'
            GROUP BY check_name, message
            ORDER BY failure_count DESC
            LIMIT 10
        """)
        
        details_data = {
            "recent_inspections": [
                {
                    "inspection_id": row[0],
                    "check_type": row[1],
                    "check_name": row[2],
                    "status": row[3],
                    "message": row[4],
                    "created_at": str(row[5])
                } for row in recent_inspections
            ],
            "check_type_statistics": [
                {
                    "check_type": row[0],
                    "total": row[1],
                    "pass_count": row[2],
                    "fail_count": row[3],
                    "pass_rate": calculate_pass_rate(row[2], row[1])
                } for row in check_type_stats
            ],
            "failure_analysis": [
                {
                    "check_name": row[0],
                    "message": row[1],
                    "failure_count": row[2]
                } for row in failure_analysis
            ]
        }
        
        return create_response_data([details_data])
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"TOS 품질 상세 데이터 조회 실패: {str(e)}"
        )

@router.get("/tos-quality-summary")
@cached(
    namespace=CacheNamespace.TOS,
    endpoint=CacheEndpoint.QUALITY_SUMMARY,
    ttl=redis_settings.CACHE_TTL_LONG  # 1시간 캐싱
)
async def get_tos_quality_summary():
    """TOS 품질 요약 데이터 (캐싱 적용: 1시간)"""
    # 디버그: 함수 진입 확인
    import logging
    logger = logging.getLogger(__name__)
    logger.info("🚨 [TOS] get_tos_quality_summary 함수 직접 실행됨!")
    
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
            WHERE inspection_id LIKE '%%berth%%'
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
            WHERE inspection_id LIKE '%%berth%%' AND check_type = 'completeness'
        """)
        
        completeness_rate = 0.0
        if completeness_stats and completeness_stats[0] > 0:
            completeness_rate = calculate_pass_rate(completeness_stats[1], completeness_stats[0])
        
        # 유효성 검사 통계
        validity_stats = execute_query_one("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count
            FROM data_inspection_results 
            WHERE inspection_id LIKE '%%berth%%' AND check_type = 'validity'
        """)
        
        validity_rate = 0.0
        if validity_stats and validity_stats[0] > 0:
            validity_rate = calculate_pass_rate(validity_stats[1], validity_stats[0])
        
        quality_data = {
            "total_inspections": total_inspections,
            "total_checks": total_checks,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate": pass_rate,
            "last_inspection_date": last_inspection.strftime('%Y-%m-%d') if last_inspection else None,
            "completeness": {
                "fields_checked": completeness_stats[0] if completeness_stats else 0,
                "pass_count": completeness_stats[1] if completeness_stats else 0,
                "fail_count": (completeness_stats[0] - completeness_stats[1]) if completeness_stats and completeness_stats[0] else 0,
                "pass_rate": completeness_rate
            },
            "validity": {
                "fields_checked": validity_stats[0] if validity_stats else 0,
                "pass_count": validity_stats[1] if validity_stats else 0,
                "fail_count": (validity_stats[0] - validity_stats[1]) if validity_stats and validity_stats[0] else 0,
                "pass_rate": validity_rate
            }
        }
        
        return create_response_data([quality_data])
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"TOS 품질 요약 조회 실패: {str(e)}"
        )

@router.get("/tos-field-analysis")
async def get_tos_field_analysis():
    """TOS 필드별 상세 분석 데이터"""
    try:
        import json
        import re
        
        # details JSON에서 필드별 통계를 추출
        all_results = execute_query("""
            SELECT 
                check_type,
                status,
                details,
                affected_rows
            FROM data_inspection_results 
            WHERE inspection_id LIKE '%%berth%%' 
            AND details IS NOT NULL AND details != ''
            ORDER BY created_at
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
            WHERE inspection_id LIKE '%%berth%%' AND severity IS NOT NULL
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
            detail=f"TOS 필드별 분석 실패: {str(e)}"
        )

@router.get("/tos-inspection-history")
async def get_tos_inspection_history(
    period: str = Query(default="daily", description="기간 타입: daily, weekly, monthly, custom"),
    start_date: Optional[str] = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="종료 날짜 (YYYY-MM-DD)")
):
    """TOS 검사 히스토리 (기간별 필터링 지원)"""
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
            WHERE (inspection_id LIKE '%%berth_inspection%%' OR inspection_id LIKE '%%berth_schedule%%')
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
            detail=f"TOS 검사 히스토리 조회 실패: {str(e)}"
        )

@router.get("/tos-data-quality-status")
async def get_tos_data_quality_status():
    """TOS 데이터 품질 상태"""
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
            WHERE (inspection_id LIKE '%%berth_inspection%%' OR inspection_id LIKE '%%berth_schedule%%')
        """)
        
        if overall_stats:
            total_inspections, total_checks, pass_count, fail_count, last_inspection = overall_stats
            pass_rate = calculate_pass_rate(pass_count, total_checks)
        else:
            total_inspections = total_checks = pass_count = fail_count = pass_rate = 0
            last_inspection = None
        
        # 알림 생성
        alerts = []
        if pass_rate < 70:
            alerts.append({
                "type": "error",
                "message": f"TOS 데이터 품질이 {pass_rate}%로 기준(70%) 미만입니다."
            })
        elif pass_rate < 80:
            alerts.append({
                "type": "warning", 
                "message": f"TOS 데이터 품질이 {pass_rate}%로 개선이 필요합니다."
            })
        
        quality_data = {
            "overall_status": "healthy" if pass_rate >= 80 else "warning" if pass_rate >= 70 else "error",
            "alerts": alerts,
            "quality_metrics": {
                "overall_rate": pass_rate,
                "total_inspections": total_inspections,
                "total_checks": total_checks,
                "pass_count": pass_count,
                "fail_count": fail_count,
                "last_inspection_date": last_inspection.strftime('%Y-%m-%d') if last_inspection else None
            }
        }
        
        return create_response_data([quality_data])
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"TOS 데이터 품질 상태 조회 실패: {str(e)}"
        )