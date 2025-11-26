from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
from pydantic import BaseModel
from datetime import datetime
import sys
import os
import time
import json

# 상위 디렉토리의 db 폴더를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from ais_service import AISService, AISInfo
from ui_data_service import UIDataService

# Pydantic 모델들
class PageVisitRequest(BaseModel):
    user_id: str
    page_name: str
    page_url: str
    login_status: str
    visit_duration: Optional[int] = None
    session_id: Optional[str] = None
    referrer: Optional[str] = None

class UIStatisticsResponse(BaseModel):
    total_visits: int
    unique_users: int
    today_visits: int

app = FastAPI(title="AIS Data API", version="1.0.0")

# CORS 설정 (React 앱과의 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용 (개발 환경용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AIS 서비스 인스턴스 생성
ais_service = AISService()
ui_service = UIDataService()

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 데이터베이스 연결"""
    if not ais_service.connect():
        print("경고: AIS 데이터베이스 연결에 실패했습니다. 샘플 데이터를 사용합니다.")
    
    if not ui_service.connect():
        print("경고: UI 데이터베이스 연결에 실패했습니다. UI 로그가 저장되지 않습니다.")

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 데이터베이스 연결 해제"""
    ais_service.disconnect()
    ui_service.disconnect()

# 미들웨어: API 호출 로그 자동 저장
@app.middleware("http")
async def log_api_calls(request: Request, call_next):
    start_time = time.time()
    
    # 요청 처리
    response = await call_next(request)
    
    # 응답 시간 계산
    response_time_ms = int((time.time() - start_time) * 1000)
    
    # API 호출 로그 저장
    try:
        # 사용자 ID 추출 (헤더에서 또는 기본값)
        user_id = request.headers.get("X-User-ID", "anonymous")
        
        # 요청 데이터 추출
        request_data = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    request_data = json.loads(body.decode())
            except:
                pass
        
        # UI 데이터베이스에 로그 저장
        ui_service.log_api_call(
            user_id=user_id,
            api_endpoint=str(request.url.path),
            http_method=request.method,
            request_data=request_data,
            response_status=response.status_code,
            response_time_ms=response_time_ms,
            session_id=request.headers.get("X-Session-ID"),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            error_message=None if response.status_code < 400 else f"HTTP {response.status_code}"
        )
    except Exception as e:
        print(f"API 호출 로그 저장 실패: {e}")
    
    return response

# Pydantic 모델들
class AISInfoResponse(BaseModel):
    id: Optional[int] = None
    mmsi_no: Optional[str] = None
    imo_no: Optional[str] = None
    vssl_nm: Optional[str] = None
    call_letter: Optional[str] = None
    vssl_tp: Optional[str] = None
    vssl_tp_cd: Optional[str] = None
    vssl_tp_crgo: Optional[str] = None
    vssl_cls: Optional[str] = None
    vssl_len: Optional[float] = None
    vssl_width: Optional[float] = None
    flag: Optional[str] = None
    flag_cd: Optional[str] = None
    vssl_def_brd: Optional[float] = None
    lon: Optional[float] = None
    lat: Optional[float] = None
    sog: Optional[float] = None
    cog: Optional[float] = None
    rot: Optional[float] = None
    head_side: Optional[float] = None
    vssl_navi: Optional[str] = None
    vssl_navi_cd: Optional[str] = None
    source: Optional[str] = None
    dt_pos_utc: Optional[str] = None
    dt_static_utc: Optional[str] = None
    vssl_tp_main: Optional[str] = None
    vssl_tp_sub: Optional[str] = None
    dst_nm: Optional[str] = None
    dst_cd: Optional[str] = None
    eta: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

class StatisticsResponse(BaseModel):
    totalShips: int
    shipTypes: List[dict]
    flags: List[dict]
    navigationStatus: List[dict]

# UI 로그 관련 Pydantic 모델들
class PageVisitRequest(BaseModel):
    user_id: str
    page_name: str
    page_url: str
    login_status: str = "visit"  # login, logout, visit
    visit_duration: Optional[int] = None
    session_id: Optional[str] = None
    referrer: Optional[str] = None

class UIStatisticsResponse(BaseModel):
    total_page_visits: int
    total_api_calls: int
    unique_users: int
    login_status_stats: List[tuple]
    most_visited_pages: List[tuple]
    most_called_apis: List[tuple]
    avg_response_time_ms: float

# API 엔드포인트들
@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "AIS Data API", "version": "1.0.0"}

@app.get("/ais/all", response_model=List[AISInfoResponse])
async def get_all_ais_data(limit: Optional[int] = None):
    """모든 AIS 데이터 조회"""
    try:
        data = ais_service.load_all_data(limit)
        return [AISInfoResponse.model_validate(item.__dict__) for item in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")

@app.get("/ais/mmsi/{mmsi}", response_model=List[AISInfoResponse])
async def get_ships_by_mmsi(mmsi: str):
    """MMSI로 선박 검색"""
    try:
        data = ais_service.load_by_mmsi(mmsi)
        return [AISInfoResponse.model_validate(item.__dict__) for item in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MMSI 검색 실패: {str(e)}")

@app.get("/ais/name/{name}", response_model=List[AISInfoResponse])
async def get_ships_by_name(name: str):
    """선박명으로 검색"""
    try:
        data = ais_service.load_by_ship_name(name)
        return [AISInfoResponse.model_validate(item.__dict__) for item in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"선박명 검색 실패: {str(e)}")

@app.get("/ais/flag/{flag}", response_model=List[AISInfoResponse])
async def get_ships_by_flag(flag: str):
    """국적별 선박 검색"""
    try:
        data = ais_service.load_by_flag(flag)
        return [AISInfoResponse.model_validate(item.__dict__) for item in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"국적별 검색 실패: {str(e)}")

@app.get("/ais/type/{ship_type}", response_model=List[AISInfoResponse])
async def get_ships_by_type(ship_type: str):
    """선박 타입별 필터링"""
    try:
        data = ais_service.filter_by_ship_type(ship_type)
        return [AISInfoResponse.model_validate(item.__dict__) for item in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"선박 타입별 검색 실패: {str(e)}")

@app.get("/ais/latest", response_model=List[AISInfoResponse])
async def get_latest_data():
    """최신 데이터 조회"""
    try:
        # 최신 데이터 100개 반환
        data = ais_service.load_all_data(100)
        return [AISInfoResponse.model_validate(item.__dict__) for item in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"최신 데이터 조회 실패: {str(e)}")

@app.get("/ais/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """통계 데이터 조회"""
    try:
        # 모든 데이터 로드
        data = ais_service.load_all_data()
        
        # 선박 타입별 통계
        ship_type_map = {}
        flag_map = {}
        nav_status_map = {}
        
        for ship in data:
            # 선박 타입
            ship_type = ship.vssl_tp or "Unknown"
            ship_type_map[ship_type] = ship_type_map.get(ship_type, 0) + 1
            
            # 국적
            flag = ship.flag or "Unknown"
            flag_map[flag] = flag_map.get(flag, 0) + 1
            
            # 항해 상태
            nav_status = ship.vssl_navi or "Unknown"
            nav_status_map[nav_status] = nav_status_map.get(nav_status, 0) + 1
        
        # 상위 10개만 반환
        ship_types = [{"shipType": k, "count": v} for k, v in sorted(ship_type_map.items(), key=lambda x: x[1], reverse=True)[:10]]
        flags = [{"flag": k, "count": v} for k, v in sorted(flag_map.items(), key=lambda x: x[1], reverse=True)[:10]]
        nav_status = [{"status": k, "count": v} for k, v in sorted(nav_status_map.items(), key=lambda x: x[1], reverse=True)[:10]]
        
        return StatisticsResponse(
            totalShips=len(data),
            shipTypes=ship_types,
            flags=flags,
            navigationStatus=nav_status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 데이터 조회 실패: {str(e)}")

# UI 로그 관련 엔드포인트들
@app.post("/ui/log/page-visit")
async def log_page_visit(request: PageVisitRequest, req: Request):
    """페이지 방문 로그 저장"""
    try:
        success = ui_service.log_page_visit(
            user_id=request.user_id,
            page_name=request.page_name,
            page_url=request.page_url,
            login_status=request.login_status,
            visit_duration=request.visit_duration,
            session_id=request.session_id,
            ip_address=req.client.host if req.client else None,
            user_agent=req.headers.get("user-agent"),
            referrer=request.referrer
        )
        
        if success:
            return {"message": "페이지 방문 로그가 저장되었습니다."}
        else:
            raise HTTPException(status_code=500, detail="로그 저장에 실패했습니다.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"페이지 방문 로그 저장 실패: {str(e)}")

@app.get("/ui/statistics", response_model=UIStatisticsResponse)
async def get_ui_statistics():
    """UI 통계 데이터 조회"""
    try:
        stats = ui_service.get_ui_statistics()
        return UIStatisticsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"UI 통계 조회 실패: {str(e)}")

@app.get("/ui/user/{user_id}/activity")
async def get_user_activity(user_id: str):
    """특정 사용자의 활동 요약"""
    try:
        activity = ui_service.get_user_activity_summary(user_id)
        return activity
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 활동 조회 실패: {str(e)}")

@app.get("/ui/logs/page-visits")
async def get_page_visits(user_id: Optional[str] = None, login_status: Optional[str] = None, limit: int = 100):
    """페이지 방문 로그 조회"""
    try:
        logs = ui_service.get_page_visits(user_id=user_id, login_status=login_status, limit=limit)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"페이지 방문 로그 조회 실패: {str(e)}")

@app.get("/ui/logs/api-calls")
async def get_api_calls(user_id: Optional[str] = None, api_endpoint: Optional[str] = None, limit: int = 100):
    """API 호출 로그 조회"""
    try:
        logs = ui_service.get_api_calls(user_id=user_id, api_endpoint=api_endpoint, limit=limit)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API 호출 로그 조회 실패: {str(e)}")



@app.get("/api/dashboard/ais-summary")
async def get_ais_summary():
    """AIS 데이터 요약 조회"""
    try:
        # MySQL에서 직접 AIS 데이터 조회
        import pymysql
        
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    vsslTp,            -- 선박 타입
                    flag,              -- 국적
                    sog,               -- 속도 (Speed Over Ground)
                    vsslNm,            -- 선박명
                    callLetter,        -- 호출부호
                    lon,               -- 경도
                    lat,               -- 위도
                    vsslLen,           -- 선박 길이
                    vsslWidth,         -- 선박 폭
                    cog,               -- 방향 (Course Over Ground)
                    created_at         -- 생성 시간
                FROM ais_info 
                WHERE vsslTp IS NOT NULL 
                AND flag IS NOT NULL 
                AND sog IS NOT NULL
                LIMIT 1000
            """)
            
            rows = cursor.fetchall()
        
        connection.close()
        
        if not rows:
            return {
                "total_ships": 0,
                "unique_ship_types": 0,
                "unique_flags": 0,
                "avg_speed": 0,
                "max_speed": 0,
                "ship_type_distribution": [],
                "flag_distribution": [],
                "speed_distribution": []
            }
        
        # 통계 계산
        total_ships = len(rows)
        
        # 선박 타입별 분포
        ship_type_map = {}
        flag_map = {}
        speed_values = []
        
        for row in rows:
            # 선박 타입
            ship_type = row[0] or "Unknown"
            ship_type_map[ship_type] = ship_type_map.get(ship_type, 0) + 1
            
            # 국적
            flag = row[1] or "Unknown"
            flag_map[flag] = flag_map.get(flag, 0) + 1
            
            # 속도 (sog가 있는 경우)
            if row[2] and row[2] > 0:
                speed_values.append(float(row[2]))
        
        # 상위 5개 선박 타입
        ship_type_distribution = [
            {"type": k, "count": v} 
            for k, v in sorted(ship_type_map.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # 상위 5개 국적
        flag_distribution = [
            {"flag": k, "count": v} 
            for k, v in sorted(flag_map.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # 속도 구간별 분포
        speed_distribution = []
        if speed_values:
            avg_speed = round(sum(speed_values) / len(speed_values), 1)
            max_speed = round(max(speed_values), 1)
            
            # 속도 구간별 카운트 (2단위로 구분)
            speed_ranges = {
                '0-2': 0,
                '2-4': 0,
                '4-6': 0,
                '6-8': 0,
                '8-10': 0,
                '10-12': 0,
                '12-14': 0,
                '14-16': 0,
                '16-18': 0,
                '18-20': 0,
                '20+': 0
            }
            
            for speed in speed_values:
                if speed <= 2:
                    speed_ranges['0-2'] += 1
                elif speed <= 4:
                    speed_ranges['2-4'] += 1
                elif speed <= 6:
                    speed_ranges['4-6'] += 1
                elif speed <= 8:
                    speed_ranges['6-8'] += 1
                elif speed <= 10:
                    speed_ranges['8-10'] += 1
                elif speed <= 12:
                    speed_ranges['10-12'] += 1
                elif speed <= 14:
                    speed_ranges['12-14'] += 1
                elif speed <= 16:
                    speed_ranges['14-16'] += 1
                elif speed <= 18:
                    speed_ranges['16-18'] += 1
                elif speed <= 20:
                    speed_ranges['18-20'] += 1
                else:
                    speed_ranges['20+'] += 1
            
            speed_distribution = [
                {"range": k, "count": v} 
                for k, v in speed_ranges.items()
            ]
        else:
            avg_speed = 0
            max_speed = 0
        
        return {
            "total_ships": total_ships,
            "unique_ship_types": len(ship_type_map),
            "unique_flags": len(flag_map),
            "avg_speed": avg_speed,
            "max_speed": max_speed,
            "ship_type_distribution": ship_type_distribution,
            "flag_distribution": flag_distribution,
            "speed_distribution": speed_distribution
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AIS 데이터 요약 조회 실패: {str(e)}")

@app.get("/api/dashboard/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "service": "backend-api"}

@app.get("/api/dashboard/recent-inspections")
async def get_recent_inspections(limit: int = 10):
    """최근 검사 결과 조회 (더미 데이터)"""
    try:
        # 실제로는 데이터베이스에서 조회해야 하지만, 현재는 더미 데이터 반환
        dummy_inspections = [
            {
                "id": "insp_001",
                "timestamp": "2025-08-26T10:00:00Z",
                "status": "completed",
                "data_source": "AIS",
                "quality_score": 95,
                "records_processed": 1500,
                "errors_found": 2
            },
            {
                "id": "insp_002", 
                "timestamp": "2025-08-26T09:30:00Z",
                "status": "completed",
                "data_source": "Berth Schedule",
                "quality_score": 88,
                "records_processed": 800,
                "errors_found": 5
            },
            {
                "id": "insp_003",
                "timestamp": "2025-08-26T09:00:00Z", 
                "status": "completed",
                "data_source": "Cargo Report",
                "quality_score": 92,
                "records_processed": 1200,
                "errors_found": 1
            }
        ]
        
        return dummy_inspections[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"최근 검사 결과 조회 실패: {str(e)}")

@app.get("/api/dashboard/quality-metrics")
async def get_quality_metrics(days: int = 7):
    """품질 메트릭 요약 조회 (더미 데이터)"""
    try:
        return {
            "overall_score": 91.5,
            "data_completeness": 94.2,
            "data_accuracy": 89.8,
            "data_timeliness": 88.5,
            "trend": "improving"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"품질 메트릭 조회 실패: {str(e)}")

@app.get("/api/dashboard/data-source-stats")
async def get_data_source_stats(days: int = 7):
    """데이터 소스별 통계 조회 (더미 데이터)"""
    try:
        return [
            {"source": "AIS", "records": 1500, "quality": 95, "status": "active"},
            {"source": "Berth Schedule", "records": 800, "quality": 88, "status": "active"},
            {"source": "Cargo Report", "records": 1200, "quality": 92, "status": "active"}
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 소스 통계 조회 실패: {str(e)}")

@app.get("/ui/statistics/time-based")
async def get_time_based_statistics(period: str = 'daily', days: int = 30):
    """시간별 통계 데이터 조회 (더미 데이터)"""
    try:
        # period 검증
        if period not in ['daily', 'weekly', 'monthly']:
            raise HTTPException(status_code=400, detail="period는 'daily', 'weekly', 'monthly' 중 하나여야 합니다.")
        
        # 더미 데이터 생성 - 더 현실적이고 부드러운 패턴
        import random
        from datetime import datetime, timedelta
        
        # 현재 날짜부터 days일 전까지의 데이터 생성
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        page_visits = []
        api_calls = []
        
        # 기본값과 트렌드를 설정하여 더 자연스러운 패턴 생성
        base_page_visits = 120
        base_api_calls = 250
        
        current_date = start_date
        day_count = 0
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # 페이지 방문 데이터 (일별) - 부드러운 변동
            if period == 'daily':
                # 주말 효과 (금,토,일은 방문자 감소)
                weekend_factor = 0.7 if current_date.weekday() >= 4 else 1.0
                
                # 기본값에 작은 변동 추가 (너무 극적이지 않게)
                page_visit_variation = random.uniform(-0.2, 0.2)  # ±20% 변동
                api_call_variation = random.uniform(-0.15, 0.15)   # ±15% 변동
                
                page_visits.append([date_str, int(base_page_visits * weekend_factor * (1 + page_visit_variation))])
                api_calls.append([date_str, int(base_api_calls * weekend_factor * (1 + api_call_variation))])
                
                # 다음 날을 위해 기본값을 약간 조정 (트렌드 반영)
                base_page_visits += random.uniform(-5, 5)
                base_api_calls += random.uniform(-10, 10)
                
                # 기본값이 너무 극단적이 되지 않도록 제한
                base_page_visits = max(80, min(160, base_page_visits))
                base_api_calls = max(200, min(300, base_api_calls))
                
            # 주별 데이터
            elif period == 'weekly':
                if current_date.weekday() == 0:  # 월요일만
                    week_str = f"{current_date.strftime('%Y-%m-%d')} (주)"
                    page_visits.append([week_str, random.randint(600, 900)])
                    api_calls.append([week_str, random.randint(1200, 1800)])
            # 월별 데이터
            elif period == 'monthly':
                if current_date.day == 1:  # 매월 1일만
                    month_str = f"{current_date.strftime('%Y-%m')} (월)"
                    page_visits.append([month_str, random.randint(2000, 3500)])
                    api_calls.append([month_str, random.randint(3000, 5000)])
            
            current_date += timedelta(days=1)
            day_count += 1
        
        return {
            "page_visits": page_visits,
            "api_calls": api_calls,
            "period": period,
            "days": days,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시간별 통계 조회 실패: {str(e)}")

@app.get("/api/dashboard/performance-trends")
async def get_performance_trends(days: int = 7):
    """성능 트렌드 데이터 조회 (더미 데이터)"""
    try:
        import random
        from datetime import datetime, timedelta
        
        # 현재 날짜부터 days일 전까지의 데이터 생성
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        trends = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            trends.append({
                "date": date_str,
                "response_time": random.randint(50, 200),
                "throughput": random.randint(1000, 5000),
                "error_rate": round(random.uniform(0.1, 2.0), 2),
                "availability": round(random.uniform(98.0, 99.9), 2)
            })
            
            current_date += timedelta(days=1)
        
        return {
            "trends": trends,
            "days": days,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"성능 트렌드 조회 실패: {str(e)}")

@app.get("/api/dashboard/api-quality")
async def get_api_quality_data():
    """API 품질 데이터 조회"""
    try:
        # MySQL에서 직접 API 품질 데이터 조회
        import pymysql
        
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN inspection_id LIKE '%_inspection_%' THEN 
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
            
            rows = cursor.fetchall()
        
        connection.close()
        
        # 결과를 딕셔너리 리스트로 변환
        api_quality_data = []
        for row in rows:
            api_quality_data.append({
                "api_type": row[0],
                "total_inspections": row[1],
                "total_checks": row[2],
                "pass_count": row[3],
                "fail_count": row[4],
                "pass_rate": float(row[5])
            })
        
        return api_quality_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API 품질 데이터 조회 실패: {str(e)}")

@app.get("/api/dashboard/ais-quality-summary")
async def get_ais_quality_summary():
    """AIS 데이터 품질 요약 정보"""
    try:
        import pymysql
        
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # AIS 관련 검사 결과만 필터링
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT inspection_id) as total_inspections,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
                    ROUND(SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pass_rate,
                    MAX(created_at) as last_inspection_date
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%ais%' 
                   OR inspection_id LIKE '%AIS%'
            """)
            
            summary_row = cursor.fetchone()
            
            # 완전성 검사 통계
            cursor.execute("""
                SELECT 
                    COUNT(*) as fields_checked,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
                FROM data_inspection_results 
                WHERE (inspection_id LIKE '%ais%' OR inspection_id LIKE '%AIS%')
                  AND check_type LIKE '%COMPLETENESS%'
            """)
            
            completeness_row = cursor.fetchone()
            
            # 유효성 검사 통계
            cursor.execute("""
                SELECT 
                    COUNT(*) as fields_checked,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
                FROM data_inspection_results 
                WHERE (inspection_id LIKE '%ais%' OR inspection_id LIKE '%AIS%')
                  AND check_type LIKE '%VALIDITY%'
            """)
            
            validity_row = cursor.fetchone()
        
        connection.close()
        
        return {
            "total_inspections": summary_row[0] if summary_row else 0,
            "total_checks": summary_row[1] if summary_row else 0,
            "pass_count": summary_row[2] if summary_row else 0,
            "fail_count": summary_row[3] if summary_row else 0,
            "pass_rate": float(summary_row[4]) if summary_row and summary_row[4] else 0.0,
            "last_inspection_date": summary_row[5].strftime('%Y-%m-%d') if summary_row and summary_row[5] else None,
            "completeness": {
                "fields_checked": completeness_row[0] if completeness_row else 0,
                "pass_count": completeness_row[1] if completeness_row else 0,
                "fail_count": completeness_row[2] if completeness_row else 0,
                "pass_rate": round(float(completeness_row[1]) * 100.0 / float(completeness_row[0]), 2) if completeness_row and completeness_row[0] > 0 else 0.0
            },
            "validity": {
                "fields_checked": validity_row[0] if validity_row else 0,
                "pass_count": validity_row[1] if validity_row else 0,
                "fail_count": validity_row[2] if validity_row else 0,
                "pass_rate": round(float(validity_row[1]) * 100.0 / float(validity_row[0]), 2) if validity_row and validity_row[0] > 0 else 0.0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AIS 품질 요약 조회 실패: {str(e)}")

@app.get("/api/dashboard/tos-quality-details")
async def get_tos_quality_details():
    """TOS 품질 상세 데이터"""
    try:
        import pymysql
        
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # TOS 완전성 검사 결과 (berth_schedule 기준)
            cursor.execute("""
                SELECT 
                    SUBSTRING(message, LOCATE('[', message) + 1, LOCATE(']', message) - LOCATE('[', message) - 1) as field_name,
                    COUNT(*) as total_count,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
                    ROUND(SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as completion_rate
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%berth_schedule%'
                  AND check_type = 'completeness'
                  AND message LIKE '%[%]%'
                GROUP BY field_name
                HAVING field_name != '' AND field_name NOT REGEXP '^[0-9]+$'
                ORDER BY field_name
            """)
            
            field_groups = []
            for row in cursor.fetchall():
                if row[0]:  # field_name이 존재하는 경우만
                    field_groups.append({
                        "name": row[0],
                        "completion_rate": float(str(row[4]))
                    })
            
            # TOS 유효성 검사 결과
            cursor.execute("""
                SELECT 
                    message,
                    COUNT(*) as total_count,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%berth_schedule%'
                  AND check_type = 'validity'
                GROUP BY message
            """)
            
            validity_checks = {}
            total_validity_checks = 0
            total_validity_passes = 0
            
            for row in cursor.fetchall():
                message = row[0]
                total_validity_checks += int(row[1])
                total_validity_passes += int(row[2])
                
                if '날짜차이' in message:
                    validity_checks['date_diff'] = {
                        "range": "D3 이내",
                        "count": int(row[1]),
                        "pass_count": int(row[2]),
                        "fail_count": int(row[3]),
                        "status": "모두 범위 내" if int(row[3]) == 0 else f"{int(row[3])}건 범위 외"
                    }
        
        connection.close()
        
        # 전체 유효성 달성률 계산 (검사 항목별 성공률)
        overall_validity_rate = round(total_validity_passes * 100.0 / total_validity_checks, 1) if total_validity_checks > 0 else 0
        
        # 전체 완전성 달성률 계산
        total_fields = len(field_groups)
        successful_fields = len([f for f in field_groups if f['completion_rate'] == 100.0])
        overall_completeness_rate = round(successful_fields * 100.0 / total_fields, 1) if total_fields > 0 else 0
        
        # 유효성 검사만의 성공 여부 판단 (완전성은 별도로 관리)
        validity_success = overall_validity_rate >= 90  # 유효성 90% 이상이면 성공
        
        # 유효성 검사 내부의 세부 검사 유형들 계산
        validity_check_types = len(validity_checks) if validity_checks else 1  # 실제 유효성 검사 유형 수
        successful_validity_types = 1 if validity_success else 0  # 유효성 검사 성공 여부
        failed_validity_types = validity_check_types - successful_validity_types
        
        # 상태 메시지 생성 (유효성만)
        if overall_validity_rate >= 90:
            status_message = f"{overall_validity_rate}% 유효성 달성 (모든 유효성 검사 통과)"
        elif overall_validity_rate >= 70:
            status_message = f"{overall_validity_rate}% 유효성 달성 (일부 유효성 검사 실패)"
        else:
            status_message = f"{overall_validity_rate}% 유효성 달성 (유효성 검사 개선 필요)"
        
        return {
            "completeness": {
                "field_groups": field_groups,
                "total_fields": total_fields,
                "successful_fields": successful_fields,
                "failed_fields": total_fields - successful_fields,
                "overall_rate": overall_completeness_rate
            },
            "validity": validity_checks,
            "overall_validity": {
                "total_check_types": validity_check_types,
                "successful_check_types": successful_validity_types,
                "failed_check_types": failed_validity_types,
                "success_rate": overall_validity_rate,
                "status": status_message,
                "validity_success": validity_success,
                "validity_rate": overall_validity_rate
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TOS 품질 상세 조회 실패: {str(e)}")

@app.get("/api/dashboard/tos-quality-summary")
async def get_tos_quality_summary():
    """TOS 품질 요약 데이터"""
    try:
        import pymysql
        
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # TOS 전체 검사 통계
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT inspection_id) as total_inspections,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
                    MAX(created_at) as last_inspection_date
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%berth_schedule%'
            """)
            
            row = cursor.fetchone()
            total_inspections = int(row[0]) if row[0] else 0
            total_checks = int(row[1]) if row[1] else 0
            pass_count = int(row[2]) if row[2] else 0
            fail_count = int(row[3]) if row[3] else 0
            last_inspection_date = row[4].strftime('%Y-%m-%d') if row[4] else None
            
            # 완전성 검사 통계
            cursor.execute("""
                SELECT 
                    COUNT(*) as completeness_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as completeness_passes,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as completeness_fails
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%berth_schedule%'
                  AND check_type = 'completeness'
            """)
            
            comp_row = cursor.fetchone()
            completeness_checks = int(comp_row[0]) if comp_row[0] else 0
            completeness_passes = int(comp_row[1]) if comp_row[1] else 0
            completeness_fails = int(comp_row[2]) if comp_row[2] else 0
            
            # 유효성 검사 통계
            cursor.execute("""
                SELECT 
                    COUNT(*) as validity_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as validity_passes,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as validity_fails
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%berth_schedule%'
                  AND check_type = 'validity'
            """)
            
            val_row = cursor.fetchone()
            validity_checks = int(val_row[0]) if val_row[0] else 0
            validity_passes = int(val_row[1]) if val_row[1] else 0
            validity_fails = int(val_row[2]) if val_row[2] else 0
        
        connection.close()
        
        # 통과율 계산
        pass_rate = round(pass_count * 100.0 / total_checks, 1) if total_checks > 0 else 0
        completeness_rate = round(completeness_passes * 100.0 / completeness_checks, 1) if completeness_checks > 0 else 0
        validity_rate = round(validity_passes * 100.0 / validity_checks, 1) if validity_checks > 0 else 0
        
        return {
            "total_inspections": total_inspections,
            "total_checks": total_checks,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate": pass_rate,
            "last_inspection_date": last_inspection_date,
            "completeness": {
                "fields_checked": completeness_checks,
                "pass_count": completeness_passes,
                "fail_count": completeness_fails,
                "pass_rate": completeness_rate
            },
            "validity": {
                "fields_checked": validity_checks,
                "pass_count": validity_passes,
                "fail_count": validity_fails,
                "pass_rate": validity_rate
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TOS 품질 요약 조회 실패: {str(e)}")

@app.get("/api/dashboard/tos-field-analysis")
async def get_tos_field_analysis():
    """TOS 필드별 상세 분석 데이터"""
    try:
        import pymysql
        
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # TOS 완전성 검사 결과
            cursor.execute("""
                SELECT 
                    SUBSTRING(message, LOCATE('[', message) + 1, LOCATE(']', message) - LOCATE('[', message) - 1) as field_name,
                    status,
                    COUNT(*) as count,
                    SUBSTRING(message, 1, 200) as message
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%berth_schedule%'
                  AND check_type = 'completeness'
                  AND message LIKE '%[%]%'
                GROUP BY field_name, status, message
                ORDER BY field_name, status
            """)
            
            completeness_results = []
            for row in cursor.fetchall():
                field_name = row[0]
                status = row[1]
                count = int(row[2])
                message = row[3]
                
                # 메시지에서 총 개수와 빈값 개수 추출
                import re
                total_match = re.search(r'전체 \[(\d+)\]개', message)
                empty_match = re.search(r'\[(\d+)\]개의 빈값', message)
                
                total = int(total_match.group(1)) if total_match else count
                empty_count = int(empty_match.group(1)) if empty_match else 0
                filled_count = total - empty_count
                
                completeness_results.append({
                    "field": field_name,
                    "group": "TOS 필드",
                    "status": status,
                    "total": total,
                    "check": filled_count,
                    "etc": empty_count,
                    "message": message,
                    "checkType": "completeness"
                })
            
            # TOS 유효성 검사 결과
            cursor.execute("""
                SELECT 
                    message,
                    status,
                    COUNT(*) as count
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%berth_schedule%'
                  AND check_type = 'validity'
                GROUP BY message, status
                ORDER BY message, status
            """)
            
            validity_results = []
            for row in cursor.fetchall():
                message = row[0]
                status = row[1]
                count = int(row[2])
                
                # 날짜 차이 검사 결과 파싱
                if '날짜차이' in message:
                    import re
                    total_match = re.search(r'전체 \((\d+)\)개', message)
                    pass_match = re.search(r'D3 이내 \((\d+)\)개', message)
                    fail_match = re.search(r'그외 \((\d+)\)개', message)
                    
                    total = int(total_match.group(1)) if total_match else count
                    pass_count = int(pass_match.group(1)) if pass_match else 0
                    fail_count = int(fail_match.group(1)) if fail_match else 0
                    
                    validity_results.append({
                        "field": "atd-ata",
                        "group": "날짜 검증",
                        "status": status,
                        "total": total,
                        "check": pass_count,
                        "etc": fail_count,
                        "message": message,
                        "checkType": "validity"
                    })
        
        connection.close()
        
        # 완전성과 유효성 결과 합치기
        all_results = completeness_results + validity_results
        
        return all_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TOS 필드별 분석 조회 실패: {str(e)}")

@app.get("/api/dashboard/tos-inspection-history")
async def get_tos_inspection_history():
    """TOS 검사 히스토리 데이터"""
    try:
        import pymysql
        
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # TOS 검사 히스토리 (개별 검사별로 그룹화)
            cursor.execute("""
                SELECT 
                    inspection_id,
                    created_at as inspection_datetime,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
                    ROUND(SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pass_rate
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%%berth_schedule%%'
                GROUP BY inspection_id, created_at
                ORDER BY created_at DESC
                LIMIT 30
            """)
            
            history_data = []
            for row in cursor.fetchall():
                inspection_id = row[0]
                inspection_datetime = row[1]
                total_checks = int(row[2]) if row[2] else 0
                pass_count = int(row[3]) if row[3] else 0
                fail_count = int(row[4]) if row[4] else 0
                pass_rate = float(row[5]) if row[5] else 0
                
                # 완전성과 유효성 비율 계산 (개별 검사별)
                cursor.execute("""
                    SELECT 
                        check_type,
                        COUNT(*) as count,
                        SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count
                    FROM data_inspection_results 
                    WHERE inspection_id = %s
                    GROUP BY check_type
                """, (inspection_id,))
                
                completeness_rate = 0
                validity_rate = 0
                
                for check_row in cursor.fetchall():
                    check_type = check_row[0]
                    count = int(check_row[1])
                    passes = int(check_row[2])
                    rate = round(passes * 100.0 / count, 1) if count > 0 else 0
                    
                    if check_type == 'completeness':
                        completeness_rate = rate
                    elif check_type == 'validity':
                        validity_rate = rate
                
                # 날짜와 시간을 분리해서 표시
                inspection_date = inspection_datetime.strftime('%Y-%m-%d %H:%M') if inspection_datetime else None
                
                history_data.append({
                    "date": inspection_date,
                    "score": pass_rate,
                    "totalChecks": total_checks,
                    "passedChecks": pass_count,
                    "failedChecks": fail_count,
                    "completenessRate": completeness_rate,
                    "validityRate": validity_rate
                })
        
        connection.close()
        
        return history_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TOS 검사 히스토리 조회 실패: {str(e)}")

@app.get("/api/dashboard/tos-data-quality-status")
async def get_tos_data_quality_status():
    """TOS 데이터 품질 상태"""
    try:
        import pymysql
        from datetime import datetime
        
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 최신 검사 결과 조회
            cursor.execute("""
                SELECT 
                    check_type,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
                    MAX(created_at) as last_check
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%berth_schedule%'
                GROUP BY check_type
            """)
            
            completeness_status = 'PASS'
            completeness_rate = 100.0
            validity_status = 'PASS'
            validity_rate = 100.0
            last_check_time = None
            
            # 전체 통과율 계산을 위한 변수
            total_all_checks = 0
            total_all_passes = 0
            
            for row in cursor.fetchall():
                check_type = row[0]
                total_checks = int(row[1])
                pass_count = int(row[2])
                fail_count = int(row[3])
                last_check = row[4]
                
                rate = round(pass_count * 100.0 / total_checks, 1) if total_checks > 0 else 0
                
                # 전체 통과율 계산을 위한 누적
                total_all_checks += total_checks
                total_all_passes += pass_count
                
                if check_type == 'completeness':
                    completeness_rate = rate
                    completeness_status = 'PASS' if rate >= 90 else 'FAIL' if rate < 70 else 'WARNING'
                elif check_type == 'validity':
                    validity_rate = rate
                    validity_status = 'PASS' if rate >= 90 else 'FAIL' if rate < 70 else 'WARNING'
                
                if last_check and (not last_check_time or last_check > last_check_time):
                    last_check_time = last_check
            
            # 전체 통과율 계산 (상단과 동일한 방식)
            overall_rate = round(total_all_passes * 100.0 / total_all_checks, 1) if total_all_checks > 0 else 0
            overall_status = 'PASS' if overall_rate >= 90 else 'FAIL' if overall_rate < 70 else 'WARNING'
            
            
            # 알림 생성
            alerts = []
            if completeness_status == 'FAIL':
                alerts.append({
                    "id": "completeness_fail",
                    "type": "error",
                    "message": "완전성 검사에서 {:.1f}% 실패했습니다. 데이터 누락 필드를 확인하세요.".format(100-completeness_rate),
                    "timestamp": last_check_time.strftime('%Y-%m-%d %H:%M:%S') if last_check_time else None
                })
            elif completeness_status == 'WARNING':
                alerts.append({
                    "id": "completeness_warning",
                    "type": "warning",
                    "message": "완전성 검사에서 {:.1f}% 실패했습니다. 일부 데이터 누락이 있습니다.".format(100-completeness_rate),
                    "timestamp": last_check_time.strftime('%Y-%m-%d %H:%M:%S') if last_check_time else None
                })
            
            if validity_status == 'FAIL':
                alerts.append({
                    "id": "validity_fail",
                    "type": "error",
                    "message": "유효성 검사에서 {:.1f}% 실패했습니다. 데이터 형식 및 범위를 확인하세요.".format(100-validity_rate),
                    "timestamp": last_check_time.strftime('%Y-%m-%d %H:%M:%S') if last_check_time else None
                })
            
            # 성공 알림도 추가
            if completeness_status == 'PASS':
                alerts.append({
                    "id": "completeness_success",
                    "type": "info",
                    "message": "완전성 검사 {:.1f}% 성공했습니다.".format(completeness_rate),
                    "timestamp": last_check_time.strftime('%Y-%m-%d %H:%M:%S') if last_check_time else None
                })
        
        connection.close()
        
        return {
            "completeness": {
                "status": completeness_status,
                "rate": completeness_rate,
                "lastCheck": last_check_time.strftime('%Y-%m-%d %H:%M:%S') if last_check_time else None
            },
            "validity": {
                "status": validity_status,
                "rate": validity_rate,
                "lastCheck": last_check_time.strftime('%Y-%m-%d %H:%M:%S') if last_check_time else None
            },
            "overall": {
                "status": overall_status,
                "score": overall_rate,
                "lastUpdate": last_check_time.strftime('%Y-%m-%d %H:%M:%S') if last_check_time else None
            },
            "alerts": alerts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TOS 데이터 품질 상태 조회 실패: {str(e)}")

@app.get("/api/dashboard/ais-quality-details")
async def get_ais_quality_details():
    """AIS 데이터 품질 상세 분석"""
    try:
        import pymysql
        
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 필드별 완성도 통계 (각 필드별로 개별 조회)
            cursor.execute("""
                SELECT 
                    REPLACE(REPLACE(SUBSTRING_INDEX(SUBSTRING_INDEX(message, '[', 2), ']', 1), '[', ''), ']', '') as field_name,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    ROUND(SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as completion_rate
                FROM data_inspection_results 
                WHERE (inspection_id LIKE '%ais%' OR inspection_id LIKE '%AIS%')
                  AND check_type = 'completeness'
                  AND message LIKE '%항목에 전체%'
                GROUP BY field_name
                ORDER BY completion_rate DESC
            """)
            
            field_groups = []
            for row in cursor.fetchall():
                if row[0]:  # field_name이 존재하는 경우만
                                    field_groups.append({
                    "name": row[0],
                    "completion_rate": float(str(row[3]))
                })
            
            # 경도/위도 검증 결과
            cursor.execute("""
                SELECT 
                    message,
                    COUNT(*) as total_count,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
                FROM data_inspection_results 
                WHERE (inspection_id LIKE '%ais%' OR inspection_id LIKE '%AIS%')
                  AND (message LIKE '%[lon]%' OR message LIKE '%[lat]%')
                  AND check_type = 'validity'
                GROUP BY message
            """)
            
            coordinate_validation = {}
            validity_check_count = 0  # 검사 항목 개수 (경도, 위도, GRID)
            validity_success_count = 0  # 성공한 검사 항목 개수
            
            for row in cursor.fetchall():
                message = row[0]
                
                if '[lon]' in message:
                    validity_check_count += 1
                    if int(row[3]) == 0:  # 실패가 0개면 성공
                        validity_success_count += 1
                    coordinate_validation['longitude'] = {
                        "range": "-180°~+180°",
                        "count": int(row[1]),
                        "pass_count": int(row[2]),
                        "fail_count": int(row[3]),
                        "status": "모두 범위 내" if int(row[3]) == 0 else f"{int(row[3])}건 범위 외"
                    }
                elif '[lat]' in message:
                    validity_check_count += 1
                    if int(row[3]) == 0:  # 실패가 0개면 성공
                        validity_success_count += 1
                    coordinate_validation['latitude'] = {
                        "range": "-90°~+90°",
                        "count": int(row[1]),
                        "pass_count": int(row[2]),
                        "fail_count": int(row[3]),
                        "status": "모두 범위 내" if int(row[3]) == 0 else f"{int(row[3])}건 범위 외"
                    }
            
            # GRID 검사 결과 (바다/육지 구분)
            cursor.execute("""
                SELECT 
                    message,
                    COUNT(*) as total_count,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
                FROM data_inspection_results 
                WHERE (inspection_id LIKE '%ais%' OR inspection_id LIKE '%AIS%')
                  AND message LIKE '%유효성-그리드%'
                  AND check_type = 'validity'
                GROUP BY message
            """)
            
            grid_validation = {}
            grid_row = cursor.fetchone()
            if grid_row:
                message = grid_row[0]
                # 메시지에서 육지/바다 개수 추출
                import re
                land_match = re.search(r'육지 \((\d+)\)', message)
                sea_match = re.search(r'바다 \((\d+)\)', message)
                
                if land_match and sea_match:
                    land_count = int(land_match.group(1))
                    sea_count = int(sea_match.group(1))
                    total_count = land_count + sea_count
                    
                    # 육지에 위치한 선박은 실패로 간주 (선박은 바다에 있어야 함)
                    fail_count = land_count  # 육지에 위치한 선박 수가 실패 수
                    pass_count = sea_count   # 바다에 위치한 선박 수가 성공 수
                    
                    # GRID 검사 항목 추가 (1개 검사 항목)
                    validity_check_count += 1
                    if land_count == 0:  # 육지에 위치한 선박이 0개면 성공
                        validity_success_count += 1
                    
                    grid_validation['grid'] = {
                        "range": "육지/바다 구분",
                        "count": total_count,
                        "land_count": land_count,
                        "sea_count": sea_count,
                        "land_percentage": round(land_count * 100.0 / total_count, 1),
                        "sea_percentage": round(sea_count * 100.0 / total_count, 1),
                        "pass_count": pass_count,
                        "fail_count": fail_count,
                        "pass_rate": round(sea_count * 100.0 / total_count, 1),
                        "status": f"바다 {sea_count}개 성공, 육지 {land_count}개 실패" if land_count > 0 else f"모든 선박이 바다에 위치 (완벽)"
                    }
        
        connection.close()
        
        # 전체 유효성 달성률 계산 (검사 항목별 성공률)
        overall_validity_rate = round(validity_success_count * 100.0 / validity_check_count, 1) if validity_check_count > 0 else 0
        
        return {
            "completeness": {
                "field_groups": field_groups
            },
            "validity": {
                **coordinate_validation,
                **grid_validation
            },
            "overall_validity": {
                "total_check_types": validity_check_count,  # 검사 항목 개수 (경도, 위도, GRID)
                "successful_check_types": validity_success_count,  # 성공한 검사 항목 개수
                "failed_check_types": validity_check_count - validity_success_count,  # 실패한 검사 항목 개수
                "success_rate": overall_validity_rate,
                "status": f"{overall_validity_rate}% 유효성 달성 ({validity_success_count}/{validity_check_count} 검사 성공)"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AIS 품질 상세 조회 실패: {str(e)}")

@app.get("/api/dashboard/ais-charts")
async def get_ais_charts():
    """AIS 차트 데이터"""
    try:
        import pymysql
        
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 지리적 위치 분포 (육지/바다) - 실제 GRID 검사 결과에서 가져오기
            cursor.execute("""
                SELECT 
                    message,
                    COUNT(*) as count
                FROM data_inspection_results 
                WHERE (inspection_id LIKE '%ais%' OR inspection_id LIKE '%AIS%')
                  AND message LIKE '%유효성-그리드%'
                GROUP BY message
            """)
            
            grid_data = cursor.fetchone()
            if grid_data and '육지' in grid_data[0] and '바다' in grid_data[0]:
                # 메시지에서 육지/바다 개수 추출
                import re
                land_match = re.search(r'육지 \((\d+)\)', grid_data[0])
                sea_match = re.search(r'바다 \((\d+)\)', grid_data[0])
                
                if land_match and sea_match:
                    land_count = int(land_match.group(1))
                    sea_count = int(sea_match.group(1))
                    total_count = land_count + sea_count
                    
                    grid_distribution = [
                        {"type": "육지", "count": land_count, "percentage": round(land_count * 100.0 / total_count, 1)},
                        {"type": "바다", "count": sea_count, "percentage": round(sea_count * 100.0 / total_count, 1)}
                    ]
                else:
                    # 기본값 사용
                    grid_distribution = [
                        {"type": "육지", "count": 450, "percentage": 50.1},
                        {"type": "바다", "count": 448, "percentage": 49.9}
                    ]
            else:
                # 기본값 사용
                grid_distribution = [
                    {"type": "육지", "count": 450, "percentage": 50.1},
                    {"type": "바다", "count": 448, "percentage": 49.9}
                ]
            
            # 검사 유형별 통과율
            cursor.execute("""
                SELECT 
                    check_type,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    ROUND(SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pass_rate
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%ais%' OR inspection_id LIKE '%AIS%'
                GROUP BY check_type
                ORDER BY pass_rate DESC
            """)
            
            check_type_results = []
            for row in cursor.fetchall():
                check_type_results.append({
                    "type": row[0],
                    "total_checks": row[1],
                    "pass_count": row[2],
                    "pass_rate": float(row[3])
                })
            
            # 전체 품질 점수 계산 (모든 AIS 검사 결과의 평균 통과율)
            cursor.execute("""
                SELECT 
                    ROUND(SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as overall_pass_rate
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%ais%' OR inspection_id LIKE '%AIS%'
            """)
            overall_score_row = cursor.fetchone()
            quality_score = float(overall_score_row[0]) if overall_score_row and overall_score_row[0] else 0.0
        
        connection.close()
        
        return {
            "grid_distribution": grid_distribution,
            "check_type_results": check_type_results,
            "quality_score": quality_score
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AIS 차트 데이터 조회 실패: {str(e)}")

@app.get("/api/dashboard/ais-inspection-history")
async def get_ais_inspection_history():
    """AIS 검사 히스토리 데이터"""
    try:
        import pymysql
        
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 검사별 히스토리 데이터 조회 (각 검사 시행별로 개별 조회)
            cursor.execute("""
                SELECT 
                    inspection_id,
                    created_at as inspection_date,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
                    ROUND(SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pass_rate,
                    SUM(CASE WHEN check_type = 'completeness' AND status = 'PASS' THEN 1 ELSE 0 END) as completeness_pass,
                    SUM(CASE WHEN check_type = 'completeness' THEN 1 ELSE 0 END) as completeness_total,
                    SUM(CASE WHEN check_type = 'validity' AND status = 'PASS' THEN 1 ELSE 0 END) as validity_pass,
                    SUM(CASE WHEN check_type = 'validity' THEN 1 ELSE 0 END) as validity_total
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%ais%' OR inspection_id LIKE '%AIS%'
                GROUP BY inspection_id, created_at
                ORDER BY created_at ASC
                LIMIT 10
            """)
            
            history_data = []
            for row in cursor.fetchall():
                completeness_rate = round(float(row[6]) * 100.0 / float(row[7]), 1) if row[7] > 0 else 0.0
                validity_rate = round(float(row[8]) * 100.0 / float(row[9]), 1) if row[9] > 0 else 0.0
                
                history_data.append({
                    "date": row[1].strftime('%Y-%m-%d %H:%M'),
                    "score": float(row[5]),
                    "totalChecks": row[2],
                    "passedChecks": row[3],
                    "failedChecks": row[4],
                    "completenessRate": completeness_rate,
                    "validityRate": validity_rate
                })
        
        connection.close()
        
        return history_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AIS 검사 히스토리 조회 실패: {str(e)}")

@app.get("/api/dashboard/data-quality-status")
async def get_data_quality_status():
    """데이터 품질 상태 및 알림 정보"""
    try:
        import pymysql
        
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 전체 품질 상태 조회
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
                    ROUND(SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pass_rate,
                    MAX(created_at) as last_update
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%ais%' OR inspection_id LIKE '%AIS%'
            """)
            
            overall_row = cursor.fetchone()
            
            # 완전성 검사 상태
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    ROUND(SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pass_rate,
                    MAX(created_at) as last_check
                FROM data_inspection_results 
                WHERE (inspection_id LIKE '%ais%' OR inspection_id LIKE '%AIS%')
                  AND check_type = 'completeness'
            """)
            
            completeness_row = cursor.fetchone()
            
            # 유효성 검사 상태
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    ROUND(SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pass_rate,
                    MAX(created_at) as last_check
                FROM data_inspection_results 
                WHERE (inspection_id LIKE '%ais%' OR inspection_id LIKE '%AIS%')
                  AND check_type = 'validity'
            """)
            
            validity_row = cursor.fetchone()
            
            # 알림 메시지 생성
            alerts = []
            
            # GRID 검사 실패 알림
            cursor.execute("""
                SELECT 
                    COUNT(*) as fail_count,
                    MAX(created_at) as timestamp
                FROM data_inspection_results 
                WHERE (inspection_id LIKE '%ais%' OR inspection_id LIKE '%AIS%')
                  AND message LIKE '%유효성-그리드%'
                  AND status = 'FAIL'
            """)
            
            grid_fail_row = cursor.fetchone()
            if grid_fail_row and grid_fail_row[0] > 0:
                alerts.append({
                    "id": "grid_fail",
                    "type": "warning",
                    "message": "GRID 검사에서 {}개 항목이 실패했습니다. 바다 위 선박은 정상적인 위치입니다.".format(grid_fail_row[0]),
                    "timestamp": grid_fail_row[1].strftime('%Y-%m-%d %H:%M:%S') if grid_fail_row[1] else None
                })
            
            # 완전성 검사 통과 알림
            if completeness_row and completeness_row[1] > 0:
                alerts.append({
                    "id": "completeness_pass",
                    "type": "info",
                    "message": "완전성 검사 {}개 필드 모두 통과했습니다.".format(completeness_row[1]),
                    "timestamp": completeness_row[3].strftime('%Y-%m-%d %H:%M:%S') if completeness_row[3] else None
                })
        
        connection.close()
        
        # 상태 결정 로직
        def get_status(pass_rate):
            if pass_rate >= 95:
                return 'PASS'
            elif pass_rate >= 70:
                return 'WARNING'
            else:
                return 'FAIL'
        
        return {
            "completeness": {
                "status": get_status(float(completeness_row[2]) if completeness_row else 0),
                "rate": float(completeness_row[2]) if completeness_row else 0,
                "lastCheck": completeness_row[3].strftime('%Y-%m-%d %H:%M:%S') if completeness_row and completeness_row[3] else None
            },
            "validity": {
                "status": get_status(float(validity_row[2]) if validity_row else 0),
                "rate": float(validity_row[2]) if validity_row else 0,
                "lastCheck": validity_row[3].strftime('%Y-%m-%d %H:%M:%S') if validity_row and validity_row[3] else None
            },
            "overall": {
                "status": get_status(float(overall_row[3]) if overall_row else 0),
                "score": float(overall_row[3]) if overall_row else 0,
                "lastUpdate": overall_row[4].strftime('%Y-%m-%d %H:%M:%S') if overall_row and overall_row[4] else None
            },
            "alerts": alerts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 품질 상태 조회 실패: {str(e)}")

@app.get("/ais/statistics")
async def get_ais_statistics():
    """AIS 통계 데이터 조회 (기존 /api/dashboard/ais-summary와 동일)"""
    try:
        # MySQL에서 직접 AIS 데이터 조회
        import pymysql
        
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    vsslTp,            -- 선박 타입
                    flag,              -- 국적
                    sog,               -- 속도 (Speed Over Ground)
                    vsslNm,            -- 선박명
                    callLetter,        -- 호출부호
                    lon,               -- 경도
                    lat,               -- 위도
                    vsslLen,           -- 선박 길이
                    vsslWidth,         -- 선박 폭
                    cog,               -- 방향 (Course Over Ground)
                    created_at         -- 생성 시간
                FROM ais_info 
                WHERE vsslTp IS NOT NULL 
                AND flag IS NOT NULL 
                AND sog IS NOT NULL
                LIMIT 1000
            """)
            
            rows = cursor.fetchall()
        
        connection.close()
        
        if not rows:
            return {
                "totalShips": 0,
                "shipTypes": [],
                "flags": [],
                "navigationStatus": []
            }
        
        # 통계 계산
        total_ships = len(rows)
        
        # 선박 타입별 통계
        ship_type_map = {}
        flag_map = {}
        nav_status_map = {}
        
        for row in rows:
            # 선박 타입
            ship_type = row[0] or "Unknown"
            ship_type_map[ship_type] = ship_type_map.get(ship_type, 0) + 1
            
            # 국적
            flag = row[1] or "Unknown"
            flag_map[flag] = flag_map.get(flag, 0) + 1
        
        # 상위 10개만 반환
        ship_types = [{"shipType": k, "count": v} for k, v in sorted(ship_type_map.items(), key=lambda x: x[1], reverse=True)[:10]]
        flags = [{"flag": k, "count": v} for k, v in sorted(flag_map.items(), key=lambda x: x[1], reverse=True)[:10]]
        
        return {
            "totalShips": total_ships,
            "shipTypes": ship_types,
            "flags": flags,
            "navigationStatus": []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AIS 통계 조회 실패: {str(e)}")

# TC (Terminal Container) 관련 API
@app.get("/api/dashboard/tc-summary")
async def get_tc_summary():
    """TC 작업 요약 정보"""
    try:
        import pymysql
        
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 전체 통계
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_work,
                    COUNT(DISTINCT tmnlId) as total_terminals,
                    COUNT(DISTINCT shpCd) as total_ships,
                    COUNT(DISTINCT cntrNo) as total_containers,
                    COUNT(DISTINCT DATE(wkTime)) as work_days
                FROM tc_work_info
            """)
            
            # TC 관련 마지막 검사 날짜 조회
            cursor.execute("""
                SELECT MAX(created_at) as last_inspection_date
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%tc_work%'
            """)
            
            inspection_row = cursor.fetchone()
            last_inspection_date = inspection_row[0].strftime('%Y-%m-%d') if inspection_row[0] else None
            
            # 전체 통계 다시 조회
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_work,
                    COUNT(DISTINCT tmnlId) as total_terminals,
                    COUNT(DISTINCT shpCd) as total_ships,
                    COUNT(DISTINCT cntrNo) as total_containers,
                    COUNT(DISTINCT DATE(wkTime)) as work_days
                FROM tc_work_info
            """)
            
            summary_row = cursor.fetchone()
            total_work = int(summary_row[0]) if summary_row[0] else 0
            total_terminals = int(summary_row[1]) if summary_row[1] else 0
            total_ships = int(summary_row[2]) if summary_row[2] else 0
            total_containers = int(summary_row[3]) if summary_row[3] else 0
            work_days = int(summary_row[4]) if summary_row[4] else 0
            
            # 최근 작업 통계 (최근 7일)
            cursor.execute("""
                SELECT 
                    COUNT(*) as recent_work,
                    COUNT(DISTINCT tmnlId) as active_terminals,
                    COUNT(DISTINCT shpCd) as active_ships
                FROM tc_work_info 
                WHERE wkTime >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            """)
            
            recent_row = cursor.fetchone()
            recent_work = int(recent_row[0]) if recent_row[0] else 0
            active_terminals = int(recent_row[1]) if recent_row[1] else 0
            active_ships = int(recent_row[2]) if recent_row[2] else 0
            
            # 작업 유형별 통계
            cursor.execute("""
                SELECT 
                    wkId,
                    COUNT(*) as count
                FROM tc_work_info 
                GROUP BY wkId
                ORDER BY count DESC
                LIMIT 10
            """)
            
            work_types = []
            for row in cursor.fetchall():
                work_types.append({
                    "workType": row[0] if row[0] else "미분류",
                    "count": int(row[1])
                })
            
            # 터미널별 통계
            cursor.execute("""
                SELECT 
                    tmnlId,
                    tmnlNm,
                    COUNT(*) as count
                FROM tc_work_info 
                GROUP BY tmnlId, tmnlNm
                ORDER BY count DESC
                LIMIT 10
            """)
            
            terminals = []
            for row in cursor.fetchall():
                terminals.append({
                    "terminalId": row[0] if row[0] else "미분류",
                    "terminalName": row[1] if row[1] else "미분류",
                    "count": int(row[2])
                })
        
        connection.close()
        
        return {
            "totalWork": total_work,
            "totalTerminals": total_terminals,
            "totalShips": total_ships,
            "totalContainers": total_containers,
            "workDays": work_days,
            "recentWork": recent_work,
            "activeTerminals": active_terminals,
            "activeShips": active_ships,
            "workTypes": work_types,
            "terminals": terminals,
            "lastInspectionDate": last_inspection_date
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TC 요약 조회 실패: {str(e)}")

@app.get("/api/dashboard/tc-work-history")
async def get_tc_work_history():
    """TC 작업 히스토리"""
    try:
        import pymysql
        
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 최근 작업 히스토리 (날짜별)
            cursor.execute("""
                SELECT 
                    DATE(wkTime) as work_date,
                    COUNT(*) as total_work,
                    COUNT(DISTINCT tmnlId) as terminals,
                    COUNT(DISTINCT shpCd) as ships,
                    COUNT(DISTINCT cntrNo) as containers
                FROM tc_work_info 
                WHERE wkTime >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                GROUP BY DATE(wkTime)
                ORDER BY work_date DESC
                LIMIT 30
            """)
            
            history_data = []
            for row in cursor.fetchall():
                work_date = str(row[0]) if row[0] else None
                total_work = int(row[1]) if row[1] else 0
                terminals = int(row[2]) if row[2] else 0
                ships = int(row[3]) if row[3] else 0
                containers = int(row[4]) if row[4] else 0
                
                history_data.append({
                    "date": work_date,
                    "totalWork": total_work,
                    "terminals": terminals,
                    "ships": ships,
                    "containers": containers
                })
        
        connection.close()
        
        return history_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TC 작업 히스토리 조회 실패: {str(e)}")

@app.get("/api/dashboard/tc-quality-status")
async def get_tc_quality_status():
    """TC 데이터 품질 상태"""
    try:
        import pymysql
        connection = pymysql.connect(host='localhost', port=3307, user='root', password='Keti1234!', database='port_database', charset='utf8mb4')
        
        with connection.cursor() as cursor:
            # 전체 검사 통계
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%tc_work%'
            """)
            
            stats_row = cursor.fetchone()
            total_checks = int(stats_row[0]) if stats_row[0] else 0
            pass_count = int(stats_row[1]) if stats_row[1] else 0
            fail_count = int(stats_row[2]) if stats_row[2] else 0
            overall_rate = round(pass_count * 100.0 / total_checks, 1) if total_checks > 0 else 0
            
            # 검사 유형별 통계
            cursor.execute("""
                SELECT 
                    check_type,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%tc_work%'
                GROUP BY check_type
            """)
            
            quality_breakdown = {}
            for row in cursor.fetchall():
                check_type = row[0]
                type_total = int(row[1])
                type_pass = int(row[2])
                type_fail = int(row[3])
                type_rate = round(type_pass * 100.0 / type_total, 1) if type_total > 0 else 0
                
                quality_breakdown[check_type] = {
                    "total": type_total,
                    "pass": type_pass,
                    "fail": type_fail,
                    "rate": type_rate
                }
            
            # 알림 생성
            alerts = []
            if quality_breakdown.get('completeness', {}).get('rate', 0) < 80:
                alerts.append({
                    "type": "warning",
                    "message": f"완전성 검사에서 {100 - quality_breakdown.get('completeness', {}).get('rate', 0):.1f}% 실패했습니다."
                })
            
            if quality_breakdown.get('consistency', {}).get('rate', 0) < 50:
                alerts.append({
                    "type": "error", 
                    "message": f"일관성 검사에서 {100 - quality_breakdown.get('consistency', {}).get('rate', 0):.1f}% 실패했습니다."
                })
            
            if overall_rate < 70:
                alerts.append({
                    "type": "error",
                    "message": f"전체 품질 점수가 {overall_rate}%로 기준(70%) 미만입니다."
                })
            elif overall_rate < 80:
                alerts.append({
                    "type": "warning",
                    "message": f"전체 품질 점수가 {overall_rate}%로 개선이 필요합니다."
                })
        
        connection.close()
        
        return {
            "overall": {
                "rate": overall_rate,
                "total": total_checks,
                "pass": pass_count,
                "fail": fail_count
            },
            "breakdown": quality_breakdown,
            "alerts": alerts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TC 품질 상태 조회 실패: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000) 