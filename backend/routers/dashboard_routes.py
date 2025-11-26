"""Dashboard routes - General dashboard APIs"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

# Import models from centralized schemas
from models import (
    LatestInspectionResults,
    InspectionData,
    FailedItemsResponse,
    FailedItemData,
    APIQualityData
)

# Import utilities
from utils import (
    get_current_timestamp,
    calculate_pass_rate,
    create_response_data,
    create_error_response
)

# Import database utilities
from config import execute_query, execute_query_one

router = APIRouter()

@router.get("/latest-inspection-results", response_model=LatestInspectionResults)
async def get_latest_inspection_results(page: str = "AIS"):
    """최신 검사 결과 조회 (페이지별)"""
    try:
        # 페이지별 inspection_id 패턴 설정
        if page == "AIS":
            pattern = "%ais_info_inspection%"
        elif page == "TOS":
            pattern = "%berth%"
        elif page == "TC":
            pattern = "%tc%"
        elif page == "QC":
            pattern = "%qc%"
        else:
            pattern = "%"
        
        # 완전성 검사 결과
        completeness_stats = execute_query_one("""
            SELECT 
                COUNT(*) as total_checks,
                SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
                COUNT(DISTINCT check_name) as fields_checked,
                MAX(created_at) as last_updated
            FROM data_inspection_results 
            WHERE inspection_id LIKE %s AND check_type = 'completeness'
        """, [pattern])
        
        # 유효성 검사 결과
        validity_stats = execute_query_one("""
            SELECT 
                COUNT(*) as total_checks,
                SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
                COUNT(DISTINCT check_name) as fields_checked,
                MAX(created_at) as last_updated
            FROM data_inspection_results 
            WHERE inspection_id LIKE %s AND check_type = 'validity'
        """, [pattern])
        
        # 완전성 데이터 처리
        if completeness_stats:
            comp_total, comp_pass, comp_fail, comp_fields, comp_updated = completeness_stats
            comp_rate = calculate_pass_rate(comp_pass, comp_total)
        else:
            comp_total = comp_pass = comp_fail = comp_fields = comp_rate = 0
            comp_updated = None
        
        # 유효성 데이터 처리
        if validity_stats:
            val_total, val_pass, val_fail, val_fields, val_updated = validity_stats
            val_rate = calculate_pass_rate(val_pass, val_total)
        else:
            val_total = val_pass = val_fail = val_fields = val_rate = 0
            val_updated = None
        
        return LatestInspectionResults(
            completeness=InspectionData(
                pass_rate=comp_rate,
                total_checks=comp_total,
                pass_count=comp_pass,
                fail_count=comp_fail,
                fields_checked=comp_fields,
                last_updated=str(comp_updated) if comp_updated else None
            ),
            validity=InspectionData(
                pass_rate=val_rate,
                total_checks=val_total,
                pass_count=val_pass,
                fail_count=val_fail,
                fields_checked=val_fields,
                last_updated=str(val_updated) if val_updated else None
            )
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"최신 검사 결과 조회 실패: {str(e)}"
        )

@router.get("/recent-inspections")
async def get_recent_inspections(limit: int = 10):
    """최근 검사 결과 조회"""
    try:
        recent_data = execute_query("""
            SELECT 
                inspection_id,
                table_name,
                inspection_status,
                start_time,
                end_time,
                processing_time_ms,
                created_at
            FROM data_inspection_info
            ORDER BY created_at DESC
            LIMIT %s
        """, [limit])
        
        inspections = []
        for row in recent_data:
            inspections.append({
                "inspection_id": row[0],
                "data_type": row[1],
                "status": row[2],
                "start_time": str(row[3]) if row[3] else None,
                "end_time": str(row[4]) if row[4] else None,
                "processing_time_ms": row[5],
                "created_at": str(row[6])
            })
        
        return create_response_data(inspections)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"최근 검사 결과 조회 실패: {str(e)}"
        )

@router.get("/quality-metrics")
async def get_quality_metrics(days: int = 7):
    """품질 메트릭 요약 조회"""
    try:
        # 지정된 기간의 품질 메트릭
        metrics_data = execute_query_one("""
            SELECT 
                COUNT(DISTINCT inspection_id) as total_inspections,
                COUNT(*) as total_checks,
                SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
                COUNT(DISTINCT DATE(created_at)) as active_days
            FROM data_inspection_results 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """, [days])
        
        if metrics_data:
            total_inspections, total_checks, pass_count, fail_count, active_days = metrics_data
            overall_rate = calculate_pass_rate(pass_count, total_checks)
        else:
            total_inspections = total_checks = pass_count = fail_count = active_days = overall_rate = 0
        
        # 데이터 타입별 메트릭
        type_metrics = execute_query("""
            SELECT 
                CASE 
                    WHEN inspection_id LIKE '%%ais%%' THEN 'AIS'
                    WHEN inspection_id LIKE '%%berth%%' THEN 'TOS'
                    WHEN inspection_id LIKE '%%tc%%' THEN 'TC'
                    WHEN inspection_id LIKE '%%qc%%' THEN 'QC'
                    ELSE 'Other'
                END as data_type,
                COUNT(*) as total_checks,
                SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count
            FROM data_inspection_results 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY data_type
        """, [days])
        
        type_stats = []
        for row in type_metrics:
            type_stats.append({
                "data_type": row[0],
                "total_checks": row[1],
                "pass_count": row[2],
                "pass_rate": calculate_pass_rate(row[2], row[1])
            })
        
        metrics = {
            "period_days": days,
            "overall_metrics": {
                "total_inspections": total_inspections,
                "total_checks": total_checks,
                "pass_count": pass_count,
                "fail_count": fail_count,
                "overall_rate": overall_rate,
                "active_days": active_days
            },
            "type_metrics": type_stats
        }
        
        return create_response_data([metrics])
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"품질 메트릭 조회 실패: {str(e)}"
        )

@router.get("/data-source-stats")
async def get_data_source_stats(days: int = 7):
    """데이터 소스별 통계 조회"""
    try:
        # 데이터 소스별 통계
        source_stats = execute_query("""
            SELECT 
                data_source,
                COUNT(DISTINCT inspection_id) as inspections,
                AVG(processing_time_ms) as avg_processing_time,
                COUNT(*) as total_records
            FROM data_inspection_info 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY data_source
        """, [days])
        
        stats_data = []
        for row in source_stats:
            stats_data.append({
                "data_source": row[0],
                "inspections": row[1],
                "avg_processing_time_ms": float(row[2]) if row[2] else 0.0,
                "total_records": row[3]
            })
        
        return create_response_data(stats_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"데이터 소스별 통계 조회 실패: {str(e)}"
        )

@router.get("/performance-trends")
async def get_performance_trends(days: int = 7):
    """성능 트렌드 데이터 조회"""
    try:
        # 일별 성능 트렌드
        daily_trends = execute_query("""
            SELECT 
                DATE(created_at) as date,
                COUNT(DISTINCT inspection_id) as inspections,
                AVG(processing_time_ms) as avg_processing_time,
                SUM(CASE WHEN inspection_status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN inspection_status = 'failed' THEN 1 ELSE 0 END) as failed
            FROM data_inspection_info 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at) ASC
        """, [days])
        
        trends_data = []
        for row in daily_trends:
            trends_data.append({
                "date": str(row[0]),
                "inspections": row[1],
                "avg_processing_time_ms": float(row[2]) if row[2] else 0.0,
                "completed": row[3],
                "failed": row[4],
                "success_rate": calculate_pass_rate(row[3], row[1])
            })
        
        return create_response_data(trends_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"성능 트렌드 조회 실패: {str(e)}"
        )

@router.get("/api-quality")
async def get_api_quality_data():
    """API 품질 데이터 조회"""
    try:
        # main_old.py와 동일한 방식으로 동적 API 타입 추출
        api_stats = execute_query("""
                SELECT 
                    CASE 
                    WHEN inspection_id LIKE '%%_inspection_%%' THEN 
                            SUBSTRING_INDEX(inspection_id, '_inspection_', 1)
                        ELSE 
                            SUBSTRING_INDEX(inspection_id, '_', 1)
                    END as api_type,
                    COUNT(DISTINCT inspection_id) as total_inspections,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
                    ROUND(SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pass_rate
                FROM data_inspection_results 
                GROUP BY api_type
                ORDER BY total_inspections DESC
            """)
            
        # 결과를 딕셔너리 리스트로 변환
        api_quality = []
        for row in api_stats:
            api_quality.append({
                    "api_type": row[0],
                    "total_inspections": row[1],
                    "total_checks": row[2],
                    "pass_count": row[3],
                    "fail_count": row[4],
                    "pass_rate": float(row[5])
                })
        
        return create_response_data(api_quality)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"API 품질 데이터 조회 실패: {str(e)}"
        )

@router.get("/data-quality-status")
async def get_data_quality_status():
    """데이터 품질 상태 및 알림 정보"""
    try:
        # 전체 품질 통계
        overall_stats = execute_query_one("""
                SELECT 
                COUNT(DISTINCT inspection_id) as total_inspections,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
                FROM data_inspection_results 
        """)
        
        if overall_stats:
            total_inspections, total_checks, pass_count, fail_count = overall_stats
            overall_rate = calculate_pass_rate(pass_count, total_checks)
        else:
            total_inspections = total_checks = pass_count = fail_count = overall_rate = 0
        
        # 알림 생성
            alerts = []
        if overall_rate < 70:
            alerts.append({
                "type": "error",
                "message": f"전체 데이터 품질이 {overall_rate}%로 기준(70%) 미만입니다.",
                "timestamp": get_current_timestamp()
            })
        elif overall_rate < 80:
                alerts.append({
                    "type": "warning",
                "message": f"전체 데이터 품질이 {overall_rate}%로 개선이 필요합니다.",
                "timestamp": get_current_timestamp()
                })
        else:
                alerts.append({
                    "type": "info",
                "message": f"데이터 품질이 {overall_rate}%로 양호합니다.",
                "timestamp": get_current_timestamp()
            })
        
        quality_status = {
            "overall_status": "healthy" if overall_rate >= 80 else "warning" if overall_rate >= 70 else "error",
            "alerts": alerts,
            "quality_metrics": {
                "overall_rate": overall_rate,
                "total_inspections": total_inspections,
                "total_checks": total_checks,
                "pass_count": pass_count,
                "fail_count": fail_count
            }
        }
        
        return create_response_data([quality_status])
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"데이터 품질 상태 조회 실패: {str(e)}"
        )

@router.get("/failed-items", response_model=FailedItemsResponse)
async def get_failed_items(page: str = "AIS"):
    """실패한 항목 데이터 조회 (페이지별)"""
    try:
        # 페이지별 패턴 설정
        if page == "AIS":
            pattern = "%ais_info_inspection%"
        elif page == "TOS":
            pattern = "%berth%"
        elif page == "TC":
            pattern = "%tc%"
        elif page == "QC":
            pattern = "%qc%"
        else:
            pattern = "%"
        
        # 실패한 항목들
        failed_items = execute_query("""
            SELECT 
                check_name,
                message,
                severity,
                affected_rows,
                created_at
            FROM data_inspection_results 
            WHERE inspection_id LIKE %s AND status = 'FAIL'
            ORDER BY created_at DESC
            LIMIT 20
        """, [pattern])
        
        # 성공한 항목들
        success_items = execute_query("""
            SELECT 
                check_name,
                message,
                severity,
                affected_rows,
                created_at
            FROM data_inspection_results 
            WHERE inspection_id LIKE %s AND status = 'PASS'
            ORDER BY created_at DESC
            LIMIT 10
        """, [pattern])
        
        failed_list = []
        for row in failed_items:
            failed_list.append(FailedItemData(
                field=row[0],
                reason="검사 실패",
                message=row[1] or "검사 실패",
                details=f"심각도: {row[2] or 'MEDIUM'}",
                affected_rows=row[3] or 0,
                created_at=str(row[4]) if row[4] else None
            ))
        
        success_list = []
        for row in success_items:
            success_list.append(FailedItemData(
                field=row[0],
                reason="검사 통과",
                message=row[1] or "검사 통과",
                details=f"심각도: {row[2] or 'LOW'}",
                affected_rows=row[3] or 0,
                created_at=str(row[4]) if row[4] else None
            ))
        
        return FailedItemsResponse(
            failed_items=failed_list,
            success_items=success_list,
            page=page
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"실패한 항목 조회 실패: {str(e)}"
        )