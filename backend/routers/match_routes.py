"""Match API routes - 선박번호 매칭 정보"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

# Import models from centralized schemas
from models import (
    StatisticsResponse,
    QualitySummaryData,
    LatestInspectionResults,
    FailedItemsResponse
)

# Import utilities
from utils import (
    get_current_timestamp,
    calculate_pass_rate,
    get_sql_date_condition,
    get_sql_group_by,
    validate_period,
    create_response_data,
    create_error_response,
    safe_float,
    safe_int
)

# Import database utilities
from config import execute_query, execute_query_one

# Import cache system
from services.cache.cache_decorator import cached
from services.cache.cache_keys import CacheNamespace, CacheEndpoint
from config.redis_config import redis_settings

router = APIRouter()

# ==================== PortMisVsslNo (PMIS→TOS 매칭) APIs ====================

@router.get("/port-vssl/summary")
@cached(
    namespace="port_vssl",
    endpoint=CacheEndpoint.SUMMARY,
    ttl=redis_settings.CACHE_TTL_LONG  # 1시간 캐싱
)
async def get_port_vssl_summary():
    """항만 선박번호 매칭 요약 조회 (PMIS→TOS) (캐싱 적용: 1시간)"""
    try:
        # 기본 통계
        stats_result = execute_query_one("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT prtAtCd) as unique_ports,
                COUNT(DISTINCT tmnlCd) as unique_terminals,
                COUNT(DISTINCT CONCAT(callYrPmis, callSignPmis)) as unique_pmis_vessels,
                COUNT(DISTINCT CONCAT(callYrTos, vsslCdTos)) as unique_tos_vessels,
                MAX(updated_at) as last_updated
            FROM vssl_Port_VsslNo
        """)
        
        if stats_result:
            total_records, unique_ports, unique_terminals, unique_pmis, unique_tos, last_updated = stats_result
        else:
            total_records = unique_ports = unique_terminals = unique_pmis = unique_tos = 0
            last_updated = None
        
        # 품질 정보
        quality_result = execute_query_one("""
            SELECT 
                COUNT(DISTINCT r.inspection_id) as total_inspections,
                COUNT(*) as total_checks,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                MAX(r.created_at) as last_inspection
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_Port_VsslNo'
        """)
        
        if quality_result:
            total_inspections, total_checks, pass_count, last_inspection = quality_result
            pass_rate = calculate_pass_rate(pass_count, total_checks)
        else:
            total_inspections = total_checks = pass_count = pass_rate = 0
            last_inspection = None
        
        # Completeness 검사 결과 조회
        completeness_result = execute_query_one("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as pass_count
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_Port_VsslNo' AND r.check_type = 'completeness'
        """)
        
        completeness_total = completeness_result[0] if completeness_result else 0
        completeness_pass = completeness_result[1] if completeness_result and completeness_result[1] is not None else 0
        completeness_rate = calculate_pass_rate(completeness_pass, completeness_total) if completeness_total > 0 else 0
        
        # Validity 검사 결과 조회
        validity_result = execute_query_one("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as pass_count
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_Port_VsslNo' AND r.check_type = 'validity'
        """)
        
        validity_total = validity_result[0] if validity_result else 0
        validity_pass = validity_result[1] if validity_result and validity_result[1] is not None else 0
        validity_rate = calculate_pass_rate(validity_pass, validity_total) if validity_total > 0 else 0
        
        fail_count = total_checks - pass_count if total_checks > 0 else 0
        
        summary_data = {
            "total_inspections": total_inspections,
            "total_checks": total_checks,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate": pass_rate,
            "last_inspection_date": last_inspection.strftime('%Y-%m-%d') if last_inspection else None,
            "completeness": {
                "rate": f"{completeness_rate:.2f}",
                "total": completeness_total,
                "passed": str(completeness_pass)
            },
            "validity": {
                "rate": f"{validity_rate:.2f}",
                "total": validity_total,
                "passed": str(validity_pass)
            },
            "usage": None
        }
        
        return create_response_data(summary_data)
        
    except Exception as e:
        return create_error_response(f"PortMisVsslNo 요약 조회 실패: {str(e)}")

@router.get("/port-vssl/latest-results")
async def get_port_vssl_latest_results():
    """항만 선박번호 매칭 최신 검사 결과 조회"""
    try:
        # Completeness 검사 결과
        completeness_result = execute_query_one("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN r.status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
            FROM data_inspection_results r
            INNER JOIN (
                SELECT inspection_id 
                FROM data_inspection_info
                WHERE data_source = 'vssl_Port_VsslNo'
                ORDER BY created_at DESC 
                LIMIT 1
            ) AS latest_inspection ON r.inspection_id = latest_inspection.inspection_id
            WHERE r.check_type = 'completeness'
        """)
        
        completeness_pass = completeness_result[1] if completeness_result and completeness_result[0] > 0 else 0
        completeness_fail = completeness_result[2] if completeness_result and completeness_result[0] > 0 else 0
        completeness_pass_rate = calculate_pass_rate(completeness_pass, completeness_pass + completeness_fail)
        
        # Validity 검사 결과  
        validity_result = execute_query_one("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN r.status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
            FROM data_inspection_results r
            INNER JOIN (
                SELECT inspection_id 
                FROM data_inspection_info
                WHERE data_source = 'vssl_Port_VsslNo'
                ORDER BY created_at DESC 
                LIMIT 1
            ) AS latest_inspection ON r.inspection_id = latest_inspection.inspection_id
            WHERE r.check_type = 'validity'
        """)
        
        validity_pass = validity_result[1] if validity_result and validity_result[0] > 0 else 0
        validity_fail = validity_result[2] if validity_result and validity_result[0] > 0 else 0
        validity_pass_rate = calculate_pass_rate(validity_pass, validity_pass + validity_fail)
        
        latest_results = {
            "completeness": {
                "passCount": completeness_pass,
                "failCount": completeness_fail,
                "passRate": completeness_pass_rate
            },
            "validity": {
                "passCount": validity_pass,
                "failCount": validity_fail,
                "passRate": validity_pass_rate
            },
            "consistency": None,
            "usage": None
        }
        
        return create_response_data(latest_results)
        
    except Exception as e:
        return create_error_response(f"최신 검사 결과 조회 실패: {str(e)}")

@router.get("/port-vssl/inspection-history")
async def get_port_vssl_inspection_history(
    period: str = Query('daily', regex='^(daily|weekly|monthly|custom)$'),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)")
):
    """항만 선박번호 매칭 검사 히스토리 조회"""
    try:
        # 기간 유효성 검증
        if not validate_period(period):
            raise ValueError(f"Invalid period: {period}")
        
        # SQL 날짜 조건 및 그룹화
        date_condition_sql, date_params = get_sql_date_condition(period, start_date, end_date)
        group_by_expr, group_by_display = get_sql_group_by(period)
        
        # created_at 컬럼을 r 테이블로 명확히 지정
        date_condition_sql_fixed = date_condition_sql.replace('created_at', 'r.created_at')
        group_by_expr_fixed = group_by_expr.replace('created_at', 'r.created_at')
        group_by_display_fixed = group_by_display.replace('created_at', 'r.created_at')
        
        query = f"""
            SELECT 
                {group_by_display_fixed} as inspection_date,
                COUNT(DISTINCT r.inspection_id) as total_inspections,
                COUNT(*) as total_checks,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN r.status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_Port_VsslNo'
            {date_condition_sql_fixed}
            GROUP BY {group_by_expr_fixed}
            ORDER BY {group_by_expr_fixed} ASC
            LIMIT 30
        """
        
        results = execute_query(query)
        
        history_data = []
        for row in results:
            inspection_date, total_inspections, total_checks, pass_count, fail_count = row
            pass_rate = calculate_pass_rate(pass_count, total_checks)
            
            history_data.append({
                "date": inspection_date,
                "score": pass_rate,  # 전체 품질 점수
                "totalChecks": total_checks,
                "passedChecks": pass_count,  # passCount → passedChecks
                "failedChecks": fail_count,  # failCount → failedChecks
                "completenessRate": pass_rate,  # 기본값으로 전체 pass_rate 사용
                "validityRate": pass_rate  # 기본값으로 전체 pass_rate 사용
            })
        
        return create_response_data(history_data)
        
    except ValueError as e:
        return create_error_response(str(e))
    except Exception as e:
        return create_error_response(f"검사 히스토리 조회 실패: {str(e)}")

@router.get("/port-vssl/field-analysis")
async def get_port_vssl_field_analysis():
    """항만 선박번호 매칭 필드별 품질 분석"""
    try:
        import json
        import re
        
        # 최신 검사 결과에서 필드별 분석
        query = """
            SELECT 
                r.check_name,
                r.check_type,
                r.status,
                COUNT(*) as check_count,
                r.affected_rows,
                r.details,
                MAX(r.created_at) as last_check
            FROM data_inspection_results r
            INNER JOIN (
                SELECT inspection_id 
                FROM data_inspection_info
                WHERE data_source = 'vssl_Port_VsslNo'
                ORDER BY created_at DESC 
                LIMIT 5
            ) AS recent_inspections ON r.inspection_id = recent_inspections.inspection_id
            GROUP BY r.check_name, r.check_type, r.status, r.affected_rows, r.details
            ORDER BY r.check_name, r.check_type
        """
        
        results = execute_query(query)
        
        # 필드별로 데이터 집계
        field_data = {}
        
        for row in results:
            check_name, check_type, status, check_count, affected_rows, details, last_check = row
            
            # details에서 실제 필드명 추출 (AIS 방식과 동일)
            actual_field_name = check_name  # 기본값
            message = ""
            
            if details:
                try:
                    details_dict = json.loads(details) if isinstance(details, str) else details
                    message = details_dict.get('message', '')
                    
                    # 메시지에서 필드명 추출: [필드명] 형식
                    match = re.search(r'\[([^\]]+)\]', message)
                    if match:
                        actual_field_name = match.group(1)
                except:
                    pass
            
            key = f"{actual_field_name}_{check_type}"
            
            if key not in field_data:
                field_data[key] = {
                    'field_name': actual_field_name,
                    'check_type': check_type,
                    'total': 0,
                    'pass_count': 0,
                    'fail_count': 0,
                    'max_affected_rows': 0,
                    'error_sum': 0,
                    'last_message': message
                }
            else:
                # 마지막 메시지 업데이트
                if message:
                    field_data[key]['last_message'] = message
            
            field_data[key]['total'] += check_count
            
            if status == 'PASS':
                field_data[key]['pass_count'] += check_count
            else:
                field_data[key]['fail_count'] += check_count
            
            # affected_rows 집계 (중복 방지)
            actual_error_count = affected_rows if affected_rows else 0
            field_data[key]['max_affected_rows'] = max(field_data[key]['max_affected_rows'], actual_error_count)
            field_data[key]['error_sum'] = field_data[key]['max_affected_rows']
        
        # 필드 통계 생성
        field_stats = []
        
        # 총 데이터 행 수 조회
        total_records_result = execute_query_one("SELECT COUNT(*) FROM vssl_Port_VsslNo")
        actual_total = total_records_result[0] if total_records_result else 0
        
        for key, data in field_data.items():
            pass_rate = calculate_pass_rate(data['pass_count'], data['total'])
            error_sum = data['error_sum']
            normal_count = actual_total - error_sum if actual_total >= error_sum else 0
            
            field_stats.append((
                data['field_name'],
                data['check_type'],
                actual_total,
                data['pass_count'],
                data['fail_count'],
                pass_rate,
                error_sum,
                data['last_message']
            ))
        
        # 응답 데이터 생성 (AIS와 동일한 구조)
        field_statistics = []
        for stat in field_stats:
            field_name, check_type, total, pass_count, fail_count, pass_rate, error_sum, last_message = stat
            
            field_statistics.append({
                "field_name": field_name,
                "check_type": check_type,
                "total_checks": total,  # 실제 데이터 행 수
                "pass_count": pass_count,
                "fail_count": fail_count,
                "pass_rate": pass_rate,
                "affected_rows": error_sum,  # 오류 개수
                "original_message": last_message
            })
        
        analysis_data = {
            "field_statistics": field_statistics,
            "severity_distribution": []
        }
        
        return create_response_data([analysis_data])
        
    except Exception as e:
        return create_error_response(f"필드 분석 실패: {str(e)}")

@router.get("/port-vssl/quality-status")
async def get_port_vssl_quality_status():
    """항만 선박번호 매칭 실시간 품질 상태"""
    try:
        # 최근 24시간 검사 결과
        query = """
            SELECT 
                r.check_type,
                COUNT(*) as total_checks,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN r.status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_Port_VsslNo'
            AND r.created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            GROUP BY r.check_type
        """
        
        results = execute_query(query)
        
        quality_status = {}
        for row in results:
            check_type, total_checks, pass_count, fail_count = row
            pass_rate = calculate_pass_rate(pass_count, total_checks)
            
            quality_status[check_type] = {
                "totalChecks": total_checks,
                "passCount": pass_count,
                "failCount": fail_count,
                "passRate": pass_rate
            }
        
        return create_response_data(quality_status)
        
    except Exception as e:
        return create_error_response(f"품질 상태 조회 실패: {str(e)}")

# ==================== TosVsslNo (TOS→PMIS 매칭) APIs ====================

@router.get("/tos-vssl/summary")
@cached(
    namespace="tos_vssl",
    endpoint=CacheEndpoint.SUMMARY,
    ttl=redis_settings.CACHE_TTL_LONG  # 1시간 캐싱
)
async def get_tos_vssl_summary():
    """TOS 선박번호 매칭 요약 조회 (TOS→PMIS) (캐싱 적용: 1시간)"""
    try:
        # 기본 통계
        stats_result = execute_query_one("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT prtAtCd) as unique_ports,
                COUNT(DISTINCT tmnlCd) as unique_terminals,
                COUNT(DISTINCT CONCAT(callYrPmis, callSignPmis)) as unique_pmis_vessels,
                COUNT(DISTINCT CONCAT(callYrTos, vsslCdTos)) as unique_tos_vessels,
                MAX(updated_at) as last_updated
            FROM vssl_Tos_VsslNo
        """)
        
        if stats_result:
            total_records, unique_ports, unique_terminals, unique_pmis, unique_tos, last_updated = stats_result
        else:
            total_records = unique_ports = unique_terminals = unique_pmis = unique_tos = 0
            last_updated = None
        
        # 품질 정보
        quality_result = execute_query_one("""
            SELECT 
                COUNT(DISTINCT r.inspection_id) as total_inspections,
                COUNT(*) as total_checks,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                MAX(r.created_at) as last_inspection
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_Tos_VsslNo'
        """)
        
        if quality_result:
            total_inspections, total_checks, pass_count, last_inspection = quality_result
            pass_rate = calculate_pass_rate(pass_count, total_checks)
        else:
            total_inspections = total_checks = pass_count = pass_rate = 0
            last_inspection = None
        
        # Completeness 검사 결과 조회
        completeness_result = execute_query_one("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as pass_count
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_Tos_VsslNo' AND r.check_type = 'completeness'
        """)
        
        completeness_total = completeness_result[0] if completeness_result else 0
        completeness_pass = completeness_result[1] if completeness_result and completeness_result[1] is not None else 0
        completeness_rate = calculate_pass_rate(completeness_pass, completeness_total) if completeness_total > 0 else 0
        
        # Validity 검사 결과 조회
        validity_result = execute_query_one("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as pass_count
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_Tos_VsslNo' AND r.check_type = 'validity'
        """)
        
        validity_total = validity_result[0] if validity_result else 0
        validity_pass = validity_result[1] if validity_result and validity_result[1] is not None else 0
        validity_rate = calculate_pass_rate(validity_pass, validity_total) if validity_total > 0 else 0
        
        fail_count = total_checks - pass_count if total_checks > 0 else 0
        
        summary_data = {
            "total_inspections": total_inspections,
            "total_checks": total_checks,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate": pass_rate,
            "last_inspection_date": last_inspection.strftime('%Y-%m-%d') if last_inspection else None,
            "completeness": {
                "rate": f"{completeness_rate:.2f}",
                "total": completeness_total,
                "passed": str(completeness_pass)
            },
            "validity": {
                "rate": f"{validity_rate:.2f}",
                "total": validity_total,
                "passed": str(validity_pass)
            },
            "usage": None
        }
        
        return create_response_data(summary_data)
        
    except Exception as e:
        return create_error_response(f"TosVsslNo 요약 조회 실패: {str(e)}")

@router.get("/tos-vssl/latest-results")
async def get_tos_vssl_latest_results():
    """TOS 선박번호 매칭 최신 검사 결과 조회"""
    try:
        # Completeness 검사 결과
        completeness_result = execute_query_one("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN r.status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
            FROM data_inspection_results r
            INNER JOIN (
                SELECT inspection_id 
                FROM data_inspection_info
                WHERE data_source = 'vssl_Tos_VsslNo'
                ORDER BY created_at DESC 
                LIMIT 1
            ) AS latest_inspection ON r.inspection_id = latest_inspection.inspection_id
            WHERE r.check_type = 'completeness'
        """)
        
        completeness_pass = completeness_result[1] if completeness_result and completeness_result[0] > 0 else 0
        completeness_fail = completeness_result[2] if completeness_result and completeness_result[0] > 0 else 0
        completeness_pass_rate = calculate_pass_rate(completeness_pass, completeness_pass + completeness_fail)
        
        # Validity 검사 결과  
        validity_result = execute_query_one("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN r.status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
            FROM data_inspection_results r
            INNER JOIN (
                SELECT inspection_id 
                FROM data_inspection_info
                WHERE data_source = 'vssl_Tos_VsslNo'
                ORDER BY created_at DESC 
                LIMIT 1
            ) AS latest_inspection ON r.inspection_id = latest_inspection.inspection_id
            WHERE r.check_type = 'validity'
        """)
        
        validity_pass = validity_result[1] if validity_result and validity_result[0] > 0 else 0
        validity_fail = validity_result[2] if validity_result and validity_result[0] > 0 else 0
        validity_pass_rate = calculate_pass_rate(validity_pass, validity_pass + validity_fail)
        
        latest_results = {
            "completeness": {
                "passCount": completeness_pass,
                "failCount": completeness_fail,
                "passRate": completeness_pass_rate
            },
            "validity": {
                "passCount": validity_pass,
                "failCount": validity_fail,
                "passRate": validity_pass_rate
            },
            "consistency": None,
            "usage": None
        }
        
        return create_response_data(latest_results)
        
    except Exception as e:
        return create_error_response(f"최신 검사 결과 조회 실패: {str(e)}")

@router.get("/tos-vssl/inspection-history")
async def get_tos_vssl_inspection_history(
    period: str = Query('daily', regex='^(daily|weekly|monthly|custom)$'),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)")
):
    """TOS 선박번호 매칭 검사 히스토리 조회"""
    try:
        # 기간 유효성 검증
        if not validate_period(period):
            raise ValueError(f"Invalid period: {period}")
        
        # SQL 날짜 조건 및 그룹화
        date_condition_sql, date_params = get_sql_date_condition(period, start_date, end_date)
        group_by_expr, group_by_display = get_sql_group_by(period)
        
        # created_at 컬럼을 r 테이블로 명확히 지정
        date_condition_sql_fixed = date_condition_sql.replace('created_at', 'r.created_at')
        group_by_expr_fixed = group_by_expr.replace('created_at', 'r.created_at')
        group_by_display_fixed = group_by_display.replace('created_at', 'r.created_at')
        
        query = f"""
            SELECT 
                {group_by_display_fixed} as inspection_date,
                COUNT(DISTINCT r.inspection_id) as total_inspections,
                COUNT(*) as total_checks,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN r.status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_Tos_VsslNo'
            {date_condition_sql_fixed}
            GROUP BY {group_by_expr_fixed}
            ORDER BY {group_by_expr_fixed} ASC
            LIMIT 30
        """
        
        results = execute_query(query)
        
        history_data = []
        for row in results:
            inspection_date, total_inspections, total_checks, pass_count, fail_count = row
            pass_rate = calculate_pass_rate(pass_count, total_checks)
            
            history_data.append({
                "date": inspection_date,
                "score": pass_rate,  # 전체 품질 점수
                "totalChecks": total_checks,
                "passedChecks": pass_count,  # passCount → passedChecks
                "failedChecks": fail_count,  # failCount → failedChecks
                "completenessRate": pass_rate,  # 기본값으로 전체 pass_rate 사용
                "validityRate": pass_rate  # 기본값으로 전체 pass_rate 사용
            })
        
        return create_response_data(history_data)
        
    except ValueError as e:
        return create_error_response(str(e))
    except Exception as e:
        return create_error_response(f"검사 히스토리 조회 실패: {str(e)}")

@router.get("/tos-vssl/field-analysis")
async def get_tos_vssl_field_analysis():
    """TOS 선박번호 매칭 필드별 품질 분석"""
    try:
        import json
        import re
        
        # 최신 검사 결과에서 필드별 분석
        query = """
            SELECT 
                r.check_name,
                r.check_type,
                r.status,
                COUNT(*) as check_count,
                r.affected_rows,
                r.details,
                MAX(r.created_at) as last_check
            FROM data_inspection_results r
            INNER JOIN (
                SELECT inspection_id 
                FROM data_inspection_info
                WHERE data_source = 'vssl_Tos_VsslNo'
                ORDER BY created_at DESC 
                LIMIT 5
            ) AS recent_inspections ON r.inspection_id = recent_inspections.inspection_id
            GROUP BY r.check_name, r.check_type, r.status, r.affected_rows, r.details
            ORDER BY r.check_name, r.check_type
        """
        
        results = execute_query(query)
        
        # 필드별로 데이터 집계
        field_data = {}
        
        for row in results:
            check_name, check_type, status, check_count, affected_rows, details, last_check = row
            
            # details에서 실제 필드명 추출 (AIS 방식과 동일)
            actual_field_name = check_name  # 기본값
            message = ""
            
            if details:
                try:
                    details_dict = json.loads(details) if isinstance(details, str) else details
                    message = details_dict.get('message', '')
                    
                    # 메시지에서 필드명 추출: [필드명] 형식
                    match = re.search(r'\[([^\]]+)\]', message)
                    if match:
                        actual_field_name = match.group(1)
                except:
                    pass
            
            key = f"{actual_field_name}_{check_type}"
            
            if key not in field_data:
                field_data[key] = {
                    'field_name': actual_field_name,
                    'check_type': check_type,
                    'total': 0,
                    'pass_count': 0,
                    'fail_count': 0,
                    'max_affected_rows': 0,
                    'error_sum': 0,
                    'last_message': message
                }
            else:
                # 마지막 메시지 업데이트
                if message:
                    field_data[key]['last_message'] = message
            
            field_data[key]['total'] += check_count
            
            if status == 'PASS':
                field_data[key]['pass_count'] += check_count
            else:
                field_data[key]['fail_count'] += check_count
            
            # affected_rows 집계 (중복 방지)
            actual_error_count = affected_rows if affected_rows else 0
            field_data[key]['max_affected_rows'] = max(field_data[key]['max_affected_rows'], actual_error_count)
            field_data[key]['error_sum'] = field_data[key]['max_affected_rows']
        
        # 필드 통계 생성
        field_stats = []
        
        # 총 데이터 행 수 조회
        total_records_result = execute_query_one("SELECT COUNT(*) FROM vssl_Tos_VsslNo")
        actual_total = total_records_result[0] if total_records_result else 0
        
        for key, data in field_data.items():
            pass_rate = calculate_pass_rate(data['pass_count'], data['total'])
            error_sum = data['error_sum']
            normal_count = actual_total - error_sum if actual_total >= error_sum else 0
            
            field_stats.append((
                data['field_name'],
                data['check_type'],
                actual_total,
                data['pass_count'],
                data['fail_count'],
                pass_rate,
                error_sum,
                data['last_message']
            ))
        
        # 응답 데이터 생성 (AIS와 동일한 구조)
        field_statistics = []
        for stat in field_stats:
            field_name, check_type, total, pass_count, fail_count, pass_rate, error_sum, last_message = stat
            
            field_statistics.append({
                "field_name": field_name,
                "check_type": check_type,
                "total_checks": total,  # 실제 데이터 행 수
                "pass_count": pass_count,
                "fail_count": fail_count,
                "pass_rate": pass_rate,
                "affected_rows": error_sum,  # 오류 개수
                "original_message": last_message
            })
        
        analysis_data = {
            "field_statistics": field_statistics,
            "severity_distribution": []
        }
        
        return create_response_data([analysis_data])
        
    except Exception as e:
        return create_error_response(f"필드 분석 실패: {str(e)}")

@router.get("/tos-vssl/quality-status")
async def get_tos_vssl_quality_status():
    """TOS 선박번호 매칭 실시간 품질 상태"""
    try:
        # 최근 24시간 검사 결과
        query = """
            SELECT 
                r.check_type,
                COUNT(*) as total_checks,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN r.status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_Tos_VsslNo'
            AND r.created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            GROUP BY r.check_type
        """
        
        results = execute_query(query)
        
        quality_status = {}
        for row in results:
            check_type, total_checks, pass_count, fail_count = row
            pass_rate = calculate_pass_rate(pass_count, total_checks)
            
            quality_status[check_type] = {
                "totalChecks": total_checks,
                "passCount": pass_count,
                "failCount": fail_count,
                "passRate": pass_rate
            }
        
        return create_response_data(quality_status)
        
    except Exception as e:
        return create_error_response(f"품질 상태 조회 실패: {str(e)}")

