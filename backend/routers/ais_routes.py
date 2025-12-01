"""AIS (Automatic Identification System) routes"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

# Import models from centralized schemas
from models import (
    AISInfoResponse,
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

# Import services
from services import ais_service

# Import Redis cache system
from services.cache.cache_decorator import cached
from services.cache.cache_keys import CacheNamespace, CacheEndpoint
from config.redis_config import redis_settings

router = APIRouter()

@router.get("/all", response_model=List[AISInfoResponse])
async def get_all_ais_data(limit: Optional[int] = None):
    """모든 AIS 데이터 조회"""
    try:
        data = ais_service.load_all_data(limit)
        
        # Convert to response model
        ais_list = []
        for item in data:
            ais_list.append(AISInfoResponse(**item))
        
        return ais_list
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"AIS 데이터 조회 실패: {str(e)}"
        )

@router.get("/mmsi/{mmsi}", response_model=List[AISInfoResponse])
async def get_ships_by_mmsi(mmsi: str):
    """MMSI로 선박 검색"""
    try:
        data = ais_service.load_by_mmsi(mmsi)
        
        ais_list = []
        for item in data:
            ais_list.append(AISInfoResponse(**item))
        
        return ais_list
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"MMSI 검색 실패: {str(e)}"
        )

@router.get("/name/{name}", response_model=List[AISInfoResponse])
async def get_ships_by_name(name: str):
    """선박명으로 검색"""
    try:
        data = ais_service.load_by_ship_name(name)
        
        ais_list = []
        for item in data:
            ais_list.append(AISInfoResponse(**item))
        
        return ais_list
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"선박명 검색 실패: {str(e)}"
        )

@router.get("/flag/{flag}", response_model=List[AISInfoResponse])
async def get_ships_by_flag(flag: str):
    """국적별 선박 검색"""
    try:
        data = ais_service.load_by_flag(flag)
        
        ais_list = []
        for item in data:
            ais_list.append(AISInfoResponse(**item))
        
        return ais_list
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"국적별 검색 실패: {str(e)}"
        )

@router.get("/type/{ship_type}", response_model=List[AISInfoResponse])
async def get_ships_by_type(ship_type: str):
    """선박 타입별 필터링"""
    try:
        data = ais_service.filter_by_ship_type(ship_type)
        
        ais_list = []
        for item in data:
            ais_list.append(AISInfoResponse(**item))
        
        return ais_list
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"선박 타입별 필터링 실패: {str(e)}"
        )

@router.get("/latest", response_model=List[AISInfoResponse])
async def get_latest_data():
    """최신 데이터 조회"""
    try:
        # 최신 100개 데이터 조회
        data = ais_service.load_all_data(100)
        
        ais_list = []
        for item in data:
            ais_list.append(AISInfoResponse(**item))
        
        return ais_list
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"최신 데이터 조회 실패: {str(e)}"
        )

@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """통계 데이터 조회"""
    try:
        # MySQL에서 통계 조회
        total_ships_result = execute_query_one("SELECT COUNT(*) FROM ais_info")
        total_ships = total_ships_result[0] if total_ships_result else 0
        
        # 선박 타입별 분포
        ship_types_result = execute_query("""
            SELECT vsslTp, COUNT(*) as count 
            FROM ais_info 
            WHERE vsslTp IS NOT NULL 
            GROUP BY vsslTp 
            ORDER BY count DESC 
            LIMIT 10
        """)
        ship_types = [{"name": row[0], "count": row[1]} for row in ship_types_result] if ship_types_result else []
        
        # 국적별 분포
        flags_result = execute_query("""
            SELECT flag, COUNT(*) as count 
            FROM ais_info 
            WHERE flag IS NOT NULL 
            GROUP BY flag 
            ORDER BY count DESC 
            LIMIT 10
        """)
        flags = [{"name": row[0], "count": row[1]} for row in flags_result] if flags_result else []
        
        # 항해 상태별 분포
        nav_status_result = execute_query("""
            SELECT vsslNavi, COUNT(*) as count 
            FROM ais_info 
            WHERE vsslNavi IS NOT NULL 
            GROUP BY vsslNavi 
            ORDER BY count DESC 
            LIMIT 10
        """)
        navigation_status = [{"name": row[0], "count": row[1]} for row in nav_status_result] if nav_status_result else []
        
        return StatisticsResponse(
            totalShips=total_ships,
            shipTypes=ship_types,
            flags=flags,
            navigationStatus=navigation_status
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"통계 조회 실패: {str(e)}"
        )

# === Dashboard API endpoints ===

@router.get("/ais-summary")
async def get_ais_summary_legacy():
    """AIS 데이터 요약 조회 (기존 경로 호환)"""
    return await get_ais_summary()

@router.get("/summary")
@cached(
    namespace=CacheNamespace.AIS,
    endpoint=CacheEndpoint.SUMMARY,
    ttl=redis_settings.CACHE_TTL_LONG  # 1시간 캐싱
)
async def get_ais_summary():
    """AIS 데이터 요약 조회 (캐싱 적용: 1시간)"""
    try:
        # AIS 기본 통계
        stats = await get_statistics()
        
        # 최신 데이터 개수
        latest_data = await get_latest_data()
        
        # 품질 정보 (MySQL에서)
        quality_result = execute_query_one("""
            SELECT 
                COUNT(DISTINCT inspection_id) as total_inspections,
                COUNT(*) as total_checks,
                SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                MAX(created_at) as last_inspection
            FROM data_inspection_results 
            WHERE inspection_id LIKE '%%ais_info_inspection%%'
        """)
        
        if quality_result:
            total_inspections, total_checks, pass_count, last_inspection = quality_result
            pass_rate = calculate_pass_rate(pass_count, total_checks)
        else:
            total_inspections = total_checks = pass_count = pass_rate = 0
            last_inspection = None
        
        summary_data = {
            "total_ships": stats.totalShips,
            "unique_ship_types": len(stats.shipTypes),
            "unique_flags": len(stats.flags),
            "latest_records": len(latest_data),
            "ship_type_distribution": stats.shipTypes[:5],  # Top 5
            "flag_distribution": stats.flags[:5],  # Top 5
            "quality_info": {
                "total_inspections": total_inspections,
                "total_checks": total_checks,
                "pass_rate": pass_rate,
                "last_inspection_date": last_inspection.strftime('%Y-%m-%d') if last_inspection else None
            }
        }
        
        return create_response_data([summary_data])
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"AIS 요약 조회 실패: {str(e)}"
        )

@router.get("/ais-quality-summary")
async def get_ais_quality_summary_legacy():
    """AIS 품질 요약 (기존 경로 호환)"""
    return await get_ais_quality_summary()

@router.get("/ais-quality-status")
async def get_ais_quality_status_legacy():
    """AIS 품질 상태 (기존 경로 호환)"""
    return await get_ais_quality_status()

@router.get("/ais-inspection-history")
async def get_ais_inspection_history_legacy(
    period: str = Query(default="daily", description="기간 타입: daily, weekly, monthly, custom"),
    start_date: Optional[str] = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="종료 날짜 (YYYY-MM-DD)")
):
    """AIS 검사 히스토리 (기존 경로 호환)"""
    return await get_ais_inspection_history(period, start_date, end_date)

@router.get("/quality-status")
async def get_ais_quality_status():
    """AIS 품질 상태 데이터 조회"""
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
            WHERE inspection_id LIKE '%%ais_info_inspection%%'
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
            WHERE inspection_id LIKE '%%ais_info_inspection%%' AND check_type = 'completeness'
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
            WHERE inspection_id LIKE '%%ais_info_inspection%%' AND check_type = 'validity'
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
            detail=f"AIS 품질 상태 조회 실패: {str(e)}"
        )

@router.get("/quality-summary")
@cached(
    namespace=CacheNamespace.AIS,
    endpoint=CacheEndpoint.QUALITY_SUMMARY,
    ttl=redis_settings.CACHE_TTL_LONG  # 1시간 캐싱
)
async def get_ais_quality_summary():
    """AIS 데이터 품질 요약 정보 (캐싱 적용: 1시간)"""
    return await get_ais_quality_status()

@router.get("/quality-details")
async def get_ais_quality_details():
    """AIS 데이터 품질 상세 분석"""
    try:
        # 최근 검사 결과 상세 정보
        recent_inspections = execute_query("""
                SELECT 
                inspection_id,
                check_type,
                check_name,
                status,
                message,
                created_at
                FROM data_inspection_results 
            WHERE inspection_id LIKE '%%ais_info_inspection%%'
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
            WHERE inspection_id LIKE '%%ais_info_inspection%%'
            GROUP BY check_type
        """)
        
        # 실패 원인별 분석
        failure_analysis = execute_query("""
            SELECT 
                check_name,
                message,
                COUNT(*) as failure_count
            FROM data_inspection_results 
            WHERE inspection_id LIKE '%%ais_info_inspection%%' AND status = 'FAIL'
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
            detail=f"AIS 품질 상세 분석 실패: {str(e)}"
        )

@router.get("/charts")
async def get_ais_charts():
    """AIS 차트 데이터"""
    try:
        # 선박 타입별 차트 데이터
        ship_type_chart = execute_query("""
            SELECT vsslTp, COUNT(*) as count 
            FROM ais_info 
            WHERE vsslTp IS NOT NULL 
            GROUP BY vsslTp 
            ORDER BY count DESC 
            LIMIT 10
        """)
        
        # 국적별 차트 데이터
        flag_chart = execute_query("""
            SELECT flag, COUNT(*) as count 
            FROM ais_info 
            WHERE flag IS NOT NULL 
            GROUP BY flag 
            ORDER BY count DESC 
            LIMIT 10
        """)
        
        # 속도 분포 차트 데이터
        speed_chart = execute_query("""
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
            ORDER BY count DESC
        """)
        
        charts_data = {
            "ship_type_distribution": [{"label": row[0], "value": row[1]} for row in ship_type_chart] if ship_type_chart else [],
            "flag_distribution": [{"label": row[0], "value": row[1]} for row in flag_chart] if flag_chart else [],
            "speed_distribution": [{"label": row[0], "value": row[1]} for row in speed_chart] if speed_chart else []
        }
        
        return create_response_data([charts_data])
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"AIS 차트 데이터 조회 실패: {str(e)}"
        )

@router.get("/inspection-history")
async def get_ais_inspection_history(
    period: str = Query(default="daily", description="기간 타입: daily, weekly, monthly, custom"),
    start_date: Optional[str] = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="종료 날짜 (YYYY-MM-DD)")
):
    """AIS 검사 히스토리 데이터 (기간별 필터링 지원)"""
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
            WHERE inspection_id LIKE '%%ais_info_inspection%%'
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
            detail=f"AIS 검사 히스토리 조회 실패: {str(e)}"
        )

@router.get("/ais-field-analysis")
async def get_ais_field_analysis():
    """AIS 필드별 상세 분석 데이터"""
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
            WHERE inspection_id LIKE '%%ais_info_inspection%%' 
            AND details IS NOT NULL AND details != ''
            AND created_at = (
                SELECT MAX(created_at) 
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%%ais_info_inspection%%'
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
                    
                    # 유효성-그리드 검사는 특별 처리
                    # (선박 데이터이므로 육지=오류, 바다=정상)
                    # affected_rows에는 바다(정상) 개수가 저장되어 있고,
                    # details.check에는 육지(오류) 개수가 저장되어 있음
                    if '유효성-그리드' in field_name or 'grid' in field_name.lower():
                        # check_count가 육지(오류) 개수
                        actual_error_count = check_count
                    else:
                        # 일반 검사는 affected_rows 사용
                        actual_error_count = affected_rows
                    
                    # 중복 집계 방지: 최대값만 저장
                    field_data[key]['max_affected_rows'] = max(field_data[key]['max_affected_rows'], actual_error_count)
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
            
            # 실제 데이터 행 수 (total)를 올바르게 사용
            actual_total = data['total']  # 실제 데이터 행 수 (예: 898)
            error_sum = data['error_sum']  # 오류 개수
            normal_count = actual_total - error_sum if actual_total >= error_sum else 0  # 정상 개수
            
            field_stats.append((
                data['field_name'],
                data['check_type'],
                actual_total,  # 실제 데이터 행 수 (898)
                data['pass_count'],  # PASS 검사 횟수
                data['fail_count'],  # FAIL 검사 횟수
                pass_rate,
                error_sum,  # 오류 데이터 행 수
                last_message  # 원본 메시지
            ))
        
        # 심각도별 통계
        severity_stats = execute_query("""
            SELECT 
                severity,
                COUNT(*) as count,
                check_type
            FROM data_inspection_results 
            WHERE inspection_id LIKE '%%ais_info_inspection%%' AND severity IS NOT NULL
            GROUP BY severity, check_type
            ORDER BY count DESC
        """)
        
        analysis_data = {
            "field_statistics": [
                {
                    "field_name": row[0],
                    "check_type": row[1],
                    "total_checks": row[2],  # 실제 검사한 레코드 수 (898)
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
            detail=f"AIS 필드별 분석 실패: {str(e)}"
        )