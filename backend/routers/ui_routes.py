"""UI routes - User Interface related APIs"""

from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

# Import models from centralized schemas
from models import (
    PageVisitRequest,
    UIStatisticsResponse,
    TimeBasedStats,
    DailyStats,
    WeeklyStats,
    MonthlyStats
)

# Import utilities
from utils import (
    get_current_timestamp,
    get_date_range,
    format_period_label,
    validate_period,
    create_response_data,
    create_error_response
)

# Import database utilities
from config import execute_query, execute_query_one, execute_insert

router = APIRouter()

@router.post("/log/page-visit")
async def log_page_visit(req: Request):
    """페이지 방문 로그 저장"""
    try:
        # Request body 명시적으로 파싱
        body = await req.body()
        import json
        try:
            data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=422, detail=f"Invalid JSON: {str(e)}")
        
        # PageVisitRequest 모델로 변환
        request = PageVisitRequest(**data)
        
        # IP 주소 및 User-Agent 추출
        ip_address = req.client.host
        user_agent = req.headers.get("user-agent", "")
        
        # 시간 정보 추출
        now = datetime.now()
        visit_hour = now.hour
        visit_weekday = now.weekday()
        
        query = """
            INSERT INTO ui_log_page_visits 
            (user_id, page_name, page_url, login_status, visit_duration, 
             session_id, ip_address, user_agent, referrer, visit_hour, visit_weekday, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = [
            request.user_id,
            request.page_name,
            request.page_url,
            request.login_status,
            request.visit_duration,
            request.session_id,
            ip_address,
            user_agent,
            request.referrer,
            visit_hour,
            visit_weekday,
            now
        ]
        
        execute_insert(query, params)
        
        return create_response_data([], "페이지 방문 로그가 성공적으로 저장되었습니다.")
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"페이지 방문 로그 저장 실패: {str(e)}"
        )

@router.get("/statistics", response_model=UIStatisticsResponse)
async def get_ui_statistics():
    """UI 통계 데이터 조회"""
    try:
        # 전체 페이지 방문 수
        total_page_visits_result = execute_query_one("SELECT COUNT(*) FROM ui_log_page_visits")
        total_page_visits = total_page_visits_result[0] if total_page_visits_result else 0
        
        # 전체 API 호출 수
        total_api_calls_result = execute_query_one("SELECT COUNT(*) FROM api_call_info")
        total_api_calls = total_api_calls_result[0] if total_api_calls_result else 0
        
        # 고유 사용자 수
        unique_users_result = execute_query_one("SELECT COUNT(DISTINCT user_id) FROM ui_log_page_visits")
        unique_users = unique_users_result[0] if unique_users_result else 0
        
        # 로그인 상태별 통계
        login_status_stats = execute_query("""
            SELECT login_status, COUNT(*) 
            FROM ui_log_page_visits 
            GROUP BY login_status
        """)
        
        # 가장 많이 방문한 페이지
        most_visited_pages = execute_query("""
            SELECT page_name, COUNT(*) as visit_count
            FROM ui_log_page_visits 
            GROUP BY page_name 
            ORDER BY visit_count DESC 
            LIMIT 5
        """)
        
        # 가장 많이 호출된 API
        most_called_apis = execute_query("""
            SELECT api_endpoint, COUNT(*) as call_count
            FROM api_call_info 
            GROUP BY api_endpoint 
            ORDER BY call_count DESC 
            LIMIT 5
        """)
        
        # 평균 응답 시간
        avg_response_time_result = execute_query_one("""
            SELECT AVG(response_time_ms) 
            FROM api_call_info 
            WHERE response_time_ms IS NOT NULL
        """)
        avg_response_time_ms = float(avg_response_time_result[0]) if avg_response_time_result and avg_response_time_result[0] else 0.0
        
        return UIStatisticsResponse(
            total_page_visits=total_page_visits,
            total_api_calls=total_api_calls,
            unique_users=unique_users,
            login_status_stats=login_status_stats,
            most_visited_pages=most_visited_pages,
            most_called_apis=most_called_apis,
            avg_response_time_ms=avg_response_time_ms
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"UI 통계 조회 실패: {str(e)}"
        )

@router.get("/user/{user_id}/activity")
async def get_user_activity(user_id: str):
    """특정 사용자의 활동 요약"""
    try:
        # 사용자 페이지 방문 통계
        page_visits = execute_query("""
            SELECT 
                COUNT(*) as total_visits,
                COUNT(DISTINCT page_name) as unique_pages,
                AVG(visit_duration) as avg_duration,
                MAX(created_at) as last_visit
            FROM ui_log_page_visits 
            WHERE user_id = %s
        """, [user_id])
        
        # 사용자가 가장 많이 방문한 페이지
        favorite_pages = execute_query("""
            SELECT page_name, COUNT(*) as visit_count
            FROM ui_log_page_visits 
            WHERE user_id = %s
            GROUP BY page_name 
            ORDER BY visit_count DESC 
            LIMIT 3
        """, [user_id])
        
        visit_stats = page_visits[0] if page_visits else (0, 0, 0, None)
        
        return create_response_data([{
            "user_id": user_id,
            "total_visits": visit_stats[0],
            "unique_pages": visit_stats[1],
            "avg_duration": float(visit_stats[2]) if visit_stats[2] else 0.0,
            "last_visit": str(visit_stats[3]) if visit_stats[3] else None,
            "favorite_pages": [{"page": row[0], "visits": row[1]} for row in favorite_pages]
        }])
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"사용자 활동 조회 실패: {str(e)}"
        )

@router.get("/logs/page-visits")
async def get_page_visits(
    user_id: Optional[str] = None,
    login_status: Optional[str] = None,
    limit: int = 100
):
    """페이지 방문 로그 조회"""
    try:
        query = """
            SELECT user_id, page_name, page_url, login_status, 
                   visit_duration, created_at, ip_address
            FROM ui_log_page_visits
            WHERE 1=1
        """
        params = []
        
        if user_id:
            query += " AND user_id = %s"
            params.append(user_id)
            
        if login_status:
            query += " AND login_status = %s"
            params.append(login_status)
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        results = execute_query(query, params)
        
        logs = []
        for row in results:
            logs.append({
                "user_id": row[0],
                "page_name": row[1],
                "page_url": row[2],
                "login_status": row[3],
                "visit_duration": row[4],
                "created_at": str(row[5]),
                "ip_address": row[6]
            })
        
        return create_response_data(logs)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"페이지 방문 로그 조회 실패: {str(e)}"
        )

@router.get("/logs/api-calls")
async def get_api_calls(
    user_id: Optional[str] = None,
    api_endpoint: Optional[str] = None,
    limit: int = 100
):
    """API 호출 로그 조회"""
    try:
        query = """
            SELECT api_endpoint, request_params, response_status_code, 
                   response_time_ms, created_at
            FROM api_call_info
            WHERE 1=1
        """
        params = []
        
        if api_endpoint:
            query += " AND api_endpoint LIKE %s"
            params.append(f"%{api_endpoint}%")
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        results = execute_query(query, params)
        
        logs = []
        for row in results:
            logs.append({
                "api_endpoint": row[0],
                "request_params": row[1],
                "response_status_code": row[2],
                "response_time_ms": row[3],
                "created_at": str(row[4])
            })
        
        return create_response_data(logs)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"API 호출 로그 조회 실패: {str(e)}"
        )

@router.get("/statistics/visitor-trends")
async def get_visitor_trends():
    """방문자 트렌드 분석 데이터 조회"""
    try:
        # 최근 30일간 일별 방문자 수
        daily_trends = execute_query("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as visits,
                COUNT(DISTINCT user_id) as unique_visitors
            FROM ui_log_page_visits 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date ASC
        """)
        
        # 시간대별 방문 패턴
        hourly_pattern = execute_query("""
            SELECT 
                visit_hour,
                COUNT(*) as visits
            FROM ui_log_page_visits 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY visit_hour
            ORDER BY visit_hour ASC
        """)
        
        # 요일별 방문 패턴
        weekday_pattern = execute_query("""
            SELECT 
                visit_weekday,
                COUNT(*) as visits
            FROM ui_log_page_visits 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY visit_weekday
            ORDER BY visit_weekday ASC
        """)
        
        trends_data = {
            "daily_trends": [{"date": str(row[0]), "visits": row[1], "unique_visitors": row[2]} for row in daily_trends],
            "hourly_pattern": [{"hour": row[0], "visits": row[1]} for row in hourly_pattern],
            "weekday_pattern": [{"weekday": row[0], "visits": row[1]} for row in weekday_pattern]
        }
        
        return create_response_data([trends_data])
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"방문자 트렌드 조회 실패: {str(e)}"
        )

@router.get("/statistics/time-based")
async def get_time_based_statistics(
    period: str = Query(default="daily", description="기간 타입: daily, weekly, monthly, custom"),
    start_date: Optional[str] = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="종료 날짜 (YYYY-MM-DD)")
):
    """시간별 통계 데이터 조회 (기간별 다른 데이터 + 사용자 정의 날짜 범위)"""
    try:
        if not validate_period(period):
            raise HTTPException(
                status_code=400, 
                detail="period는 'daily', 'weekly', 'monthly', 'custom' 중 하나여야 합니다."
            )
        
        # 날짜 조건 설정
        if period == 'custom' and start_date and end_date:
            date_condition = "AND DATE(pv.created_at) BETWEEN %s AND %s"
            api_date_condition = "AND DATE(created_at) BETWEEN %s AND %s"
            params = [start_date, end_date, start_date, end_date]
        elif period == 'daily':
            date_condition = "AND pv.created_at >= DATE_SUB(NOW(), INTERVAL 14 DAY)"
            api_date_condition = "AND created_at >= DATE_SUB(NOW(), INTERVAL 14 DAY)"
            params = []
        elif period == 'weekly':
            date_condition = "AND pv.created_at >= DATE_SUB(NOW(), INTERVAL 12 WEEK)"
            api_date_condition = "AND created_at >= DATE_SUB(NOW(), INTERVAL 12 WEEK)"
            params = []
        elif period == 'monthly':
            date_condition = "AND pv.created_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)"
            api_date_condition = "AND created_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)"
            params = []
        
        if period == 'daily' or period == 'custom':
            # 일별 데이터
            query = f"""
                SELECT 
                    DATE(pv.created_at) as period_date,
                    COUNT(pv.id) as page_visits,
                    COUNT(DISTINCT pv.user_id) as unique_users,
                    COALESCE(api_calls, 0) as api_calls
                FROM ui_log_page_visits pv
                LEFT JOIN (
                    SELECT DATE(created_at) as api_date, COUNT(*) as api_calls
                    FROM api_call_info 
                    WHERE 1=1 {api_date_condition}
                    GROUP BY DATE(created_at)
                ) api ON DATE(pv.created_at) = api.api_date
                WHERE 1=1 {date_condition}
                GROUP BY DATE(pv.created_at)
                ORDER BY DATE(pv.created_at) ASC
            """
            
        elif period == 'weekly':
            # 주별 데이터 (월 기준 주차)
            query = f"""
                SELECT 
                    CONCAT(YEAR(pv.created_at), '년 ', LPAD(MONTH(pv.created_at), 2, '0'), '월 ', 
                           (WEEK(pv.created_at, 1) - WEEK(DATE_SUB(pv.created_at, INTERVAL DAY(pv.created_at)-1 DAY), 1) + 1), '주차') as period_label,
                    COUNT(pv.id) as page_visits,
                    COUNT(DISTINCT pv.user_id) as unique_users,
                    COALESCE(SUM(api_calls), 0) as api_calls
                FROM ui_log_page_visits pv
                LEFT JOIN (
                    SELECT 
                        YEARWEEK(created_at, 1) as api_week,
                        COUNT(*) as api_calls
                    FROM api_call_info 
                    WHERE 1=1 {api_date_condition}
                    GROUP BY YEARWEEK(created_at, 1)
                ) api ON YEARWEEK(pv.created_at, 1) = api.api_week
                WHERE 1=1 {date_condition}
                GROUP BY YEARWEEK(pv.created_at, 1), YEAR(pv.created_at), MONTH(pv.created_at)
                ORDER BY YEARWEEK(pv.created_at, 1) ASC
            """
            
        elif period == 'monthly':
            # 월별 데이터
            query = f"""
                SELECT 
                    DATE_FORMAT(pv.created_at, '%%Y년 %%m월') as period_label,
                    COUNT(pv.id) as page_visits,
                    COUNT(DISTINCT pv.user_id) as unique_users,
                    COALESCE(SUM(api_calls), 0) as api_calls
                FROM ui_log_page_visits pv
                LEFT JOIN (
                    SELECT 
                        DATE_FORMAT(created_at, '%%Y-%%m') as api_month,
                        COUNT(*) as api_calls
                    FROM api_call_info 
                    WHERE 1=1 {api_date_condition}
                    GROUP BY DATE_FORMAT(created_at, '%%Y-%%m')
                ) api ON DATE_FORMAT(pv.created_at, '%%Y-%%m') = api.api_month
                WHERE 1=1 {date_condition}
                GROUP BY DATE_FORMAT(pv.created_at, '%%Y-%%m')
                ORDER BY DATE_FORMAT(pv.created_at, '%%Y-%%m') ASC
            """
        
        results = execute_query(query, params)
        
        data = []
        for row in results:
            data.append({
                "period": str(row[0]),
                "page_visits": int(row[1]),
                "unique_users": int(row[2]),
                "api_calls": int(row[3])
            })
        
        return create_response_data([{
            "period": period,
            "data": data
        }])
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"시간별 통계 조회 실패: {str(e)}"
        )
