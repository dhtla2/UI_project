"""VsslSpecInfo (선박 제원 정보) routes"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

# Import models from centralized schemas
from models import (
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

router = APIRouter()

@router.get("/vssl-spec/summary")
async def get_vssl_spec_summary():
    """VsslSpecInfo 품질 요약 데이터"""
    try:
        # 전체 검사 통계
        total_stats = execute_query_one("""
            SELECT 
                COUNT(DISTINCT r.inspection_id) as total_inspections,
                COUNT(*) as total_checks,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN r.status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_spec_info'
        """)
        
        if not total_stats:
            return create_response_data({
                "total_inspections": 0,
                "total_checks": 0,
                "pass_count": 0,
                "fail_count": 0,
                "pass_rate": 0,
                "last_inspection_date": None,
                "completeness": {"rate": "0.00", "total": 0, "passed": "0"},
                "validity": {"rate": "0.00", "total": 0, "passed": "0"},
                "usage": None
            })
        
        total_inspections = total_stats[0] or 0
        total_checks = total_stats[1] or 0
        pass_count = total_stats[2] or 0
        fail_count = total_stats[3] or 0
        pass_rate = calculate_pass_rate(pass_count, total_checks)
        
        # 최근 검사 날짜
        last_inspection = execute_query_one("""
            SELECT MAX(r.created_at) as last_inspection
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_spec_info'
        """)
        
        last_inspection_date = last_inspection[0] if last_inspection and last_inspection[0] else None
        
        # 완전성 검사 통계
        completeness_result = execute_query_one("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as passed
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_spec_info' 
            AND r.check_type = 'completeness'
        """)
        
        completeness_total = completeness_result[0] if completeness_result and completeness_result[0] else 0
        completeness_pass = completeness_result[1] if completeness_result and completeness_result[1] else 0
        completeness_rate = calculate_pass_rate(completeness_pass, completeness_total)
        
        # 유효성 검사 통계
        validity_result = execute_query_one("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as passed
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_spec_info' 
            AND r.check_type = 'validity'
        """)
        
        validity_total = validity_result[0] if validity_result and validity_result[0] else 0
        validity_pass = validity_result[1] if validity_result and validity_result[1] else 0
        validity_rate = calculate_pass_rate(validity_pass, validity_total)
        
        summary_data = {
            "total_inspections": total_inspections,
            "total_checks": total_checks,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate": pass_rate,
            "last_inspection_date": last_inspection_date.strftime('%Y-%m-%d') if last_inspection_date else None,
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
        print(f"VsslSpecInfo summary 오류: {e}")
        return create_error_response(f"VsslSpecInfo 요약 데이터 조회 실패: {str(e)}")

@router.get("/vssl-spec/latest-results")
async def get_vssl_spec_latest_results():
    """VsslSpecInfo 최신 검사 결과"""
    try:
        latest_results = execute_query("""
            SELECT 
                r.inspection_id,
                r.check_type,
                r.check_name,
                r.status,
                r.message,
                r.affected_rows,
                r.created_at
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_spec_info'
            ORDER BY r.created_at DESC
            LIMIT 20
        """)
        
        results = []
        for row in latest_results:
            results.append({
                "inspection_id": row[0],
                "check_type": row[1],
                "check_name": row[2],
                "status": row[3],
                "message": row[4],
                "affected_rows": row[5],
                "created_at": row[6].isoformat() if row[6] else None
            })
        
        return create_response_data(results)
        
    except Exception as e:
        print(f"VsslSpecInfo latest results 오류: {e}")
        return create_error_response(f"VsslSpecInfo 최신 결과 조회 실패: {str(e)}")

@router.get("/vssl-spec/inspection-history")
async def get_vssl_spec_inspection_history(
    period: str = Query("daily", description="조회 기간 (daily, weekly, monthly)"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)")
):
    """VsslSpecInfo 검사 히스토리"""
    try:
        # 기간 유효성 검사
        validate_period(period)
        
        # 날짜 조건 및 그룹화 설정
        date_condition_raw, date_params = get_sql_date_condition(period, start_date, end_date)
        group_by_raw, date_format_raw = get_sql_group_by(period)
        
        # JOIN 사용으로 인해 테이블 별칭 추가 필요
        date_condition = date_condition_raw.replace('created_at', 'r.created_at')
        group_by = group_by_raw.replace('created_at', 'r.created_at')
        date_format = date_format_raw.replace('created_at', 'r.created_at')
        
        # 검사 히스토리 조회
        base_query = f"""
            SELECT 
                {date_format} as inspection_date,
                {group_by} as period_key,
                COUNT(DISTINCT r.inspection_id) as total_inspections,
                COUNT(*) as total_checks,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN r.status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
                SUM(CASE WHEN r.check_type = 'completeness' AND r.status = 'PASS' THEN 1 ELSE 0 END) as completeness_pass,
                SUM(CASE WHEN r.check_type = 'completeness' THEN 1 ELSE 0 END) as completeness_total,
                SUM(CASE WHEN r.check_type = 'validity' AND r.status = 'PASS' THEN 1 ELSE 0 END) as validity_pass,
                SUM(CASE WHEN r.check_type = 'validity' THEN 1 ELSE 0 END) as validity_total
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_spec_info'
            {date_condition}
            GROUP BY {group_by}
            ORDER BY period_key DESC
            LIMIT 30
        """
        
        history_data = execute_query(base_query, date_params) if date_params else execute_query(base_query)
        
        results = []
        for row in history_data:
            inspection_date = row[0]
            # period_key = row[1]  # 정렬용
            total_inspections = row[2] or 0
            total_checks = row[3] or 0
            pass_count = row[4] or 0
            fail_count = row[5] or 0
            completeness_pass = row[6] or 0
            completeness_total = row[7] or 0
            validity_pass = row[8] or 0
            validity_total = row[9] or 0
            
            pass_rate = calculate_pass_rate(pass_count, total_checks)
            completeness_rate = calculate_pass_rate(completeness_pass, completeness_total)
            validity_rate = calculate_pass_rate(validity_pass, validity_total)
            
            results.append({
                "date": inspection_date,
                "score": pass_rate,
                "totalChecks": total_checks,
                "passedChecks": pass_count,
                "failedChecks": fail_count,
                "completenessRate": completeness_rate,
                "validityRate": validity_rate
            })
        
        return create_response_data(results)
        
    except Exception as e:
        print(f"VsslSpecInfo inspection history 오류: {e}")
        return create_error_response(f"VsslSpecInfo 검사 히스토리 조회 실패: {str(e)}")

@router.get("/vssl-spec/field-analysis")
async def get_vssl_spec_field_analysis():
    """VsslSpecInfo 필드별 상세 분석"""
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
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_spec_info'
            AND details IS NOT NULL AND details != ''
            AND r.created_at = (
                SELECT MAX(r2.created_at) 
                FROM data_inspection_results r2
                INNER JOIN data_inspection_info i2 ON r2.inspection_id = i2.inspection_id
                WHERE i2.data_source = 'vssl_spec_info'
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
                
                # 필드별 키 생성
                key = f"{field_name}_{check_type}"
                
                if key not in field_data:
                    field_data[key] = {
                        'field_name': field_name,
                        'check_type': check_type,
                        'total': total,
                        'pass_count': 0,
                        'fail_count': 0,
                        'max_affected_rows': 0,
                        'last_message': message
                    }
                else:
                    field_data[key]['last_message'] = message
                
                # 상태별 집계
                if status == 'PASS':
                    field_data[key]['pass_count'] += 1
                else:
                    field_data[key]['fail_count'] += 1
                    field_data[key]['max_affected_rows'] = max(field_data[key]['max_affected_rows'], affected_rows)
                    
            except (json.JSONDecodeError, ValueError) as e:
                continue
        
        # 리스트로 변환
        field_stats = []
        for key, data in field_data.items():
            total_checks = data['pass_count'] + data['fail_count']
            pass_rate = (data['pass_count'] * 100.0 / total_checks) if total_checks > 0 else 0
            
            field_stats.append((
                data['field_name'],
                data['check_type'],
                data['total'],
                data['pass_count'],
                data['fail_count'],
                pass_rate,
                data['max_affected_rows'],
                data['last_message']
            ))
        
        analysis_data = {
            "field_statistics": [
                {
                    "field_name": row[0],
                    "check_type": row[1],
                    "total_checks": row[2],
                    "pass_count": row[3],
                    "fail_count": row[4],
                    "pass_rate": float(row[5]),
                    "affected_rows": row[6],
                    "original_message": row[7] if len(row) > 7 else ""
                } for row in field_stats
            ],
            "severity_distribution": []
        }
        
        return create_response_data([analysis_data])
        
    except Exception as e:
        print(f"VsslSpecInfo field analysis 오류: {e}")
        return create_error_response(f"VsslSpecInfo 필드 분석 조회 실패: {str(e)}")

@router.get("/vssl-spec/quality-status")
async def get_vssl_spec_quality_status():
    """VsslSpecInfo 데이터 품질 상태"""
    try:
        # 현재 품질 상태 조회
        quality_status = execute_query_one("""
            SELECT 
                COUNT(DISTINCT r.inspection_id) as total_inspections,
                COUNT(*) as total_checks,
                SUM(CASE WHEN r.status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN r.status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
                MAX(r.created_at) as last_check
            FROM data_inspection_results r
            INNER JOIN data_inspection_info i ON r.inspection_id = i.inspection_id
            WHERE i.data_source = 'vssl_spec_info'
            AND r.created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        """)
        
        if not quality_status:
            return create_response_data({
                "status": "no_data",
                "message": "최근 24시간 내 검사 데이터가 없습니다.",
                "last_check": None,
                "total_checks": 0,
                "pass_rate": 0
            })
        
        total_inspections = quality_status[0] or 0
        total_checks = quality_status[1] or 0
        pass_count = quality_status[2] or 0
        fail_count = quality_status[3] or 0
        last_check = quality_status[4]
        pass_rate = calculate_pass_rate(pass_count, fail_count)
        
        # 상태 결정
        if pass_rate >= 95:
            status = "excellent"
            message = "데이터 품질이 우수합니다."
        elif pass_rate >= 80:
            status = "good"
            message = "데이터 품질이 양호합니다."
        elif pass_rate >= 60:
            status = "warning"
            message = "데이터 품질에 주의가 필요합니다."
        else:
            status = "critical"
            message = "데이터 품질이 심각한 수준입니다."
        
        return create_response_data({
            "status": status,
            "message": message,
            "last_check": last_check.isoformat() if last_check else None,
            "total_checks": total_checks,
            "pass_rate": pass_rate
        })
        
    except Exception as e:
        print(f"VsslSpecInfo quality status 오류: {e}")
        return create_error_response(f"VsslSpecInfo 품질 상태 조회 실패: {str(e)}")
