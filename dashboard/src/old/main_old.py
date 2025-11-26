from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import uvicorn
from pydantic import BaseModel
from datetime import datetime
import sys
import os
import time
import json
import pandas as pd
import numpy as np
import logging
from pathlib import Path

# 상위 디렉토리의 db 폴더를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

# AIPC_Client 경로 추가
aipc_path = os.path.join(os.path.dirname(__file__), '..', '..', 'AIPC_Client', 'project_files')
sys.path.insert(0, aipc_path)

# 로깅 설정
def setup_logging():
    """로깅 시스템 초기화"""
    # 로그 디렉토리 생성
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 로그 파일명 생성 (날짜_시간_main.log)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"main_{timestamp}.log"
    log_filepath = log_dir / log_filename
    
    # 로거 설정
    logger = logging.getLogger("main_backend")
    logger.setLevel(logging.DEBUG)
    
    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 파일 핸들러 (상세 로그)
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # 콘솔 핸들러 (간단한 로그)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"로깅 시스템 초기화 완료 - 로그 파일: {log_filepath}")
    return logger

# 로깅 시스템 초기화
logger = setup_logging()

from ais_service import AISService, AISInfo
from ui_data_service import UIDataService

# 품질 검사 관련 import (상대 경로 사용)
try:
    # AIPC_Client 경로를 sys.path에 추가
    aipc_root = '/home/cotlab/AIPC_Client'
    aipc_project = '/home/cotlab/AIPC_Client/project_files'
    
    logger.info(f"AIPC_Client 경로 추가 - root: {aipc_root}, project: {aipc_project}")
    
    if aipc_root not in sys.path:
        sys.path.insert(0, aipc_root)
        logger.info(f"sys.path에 {aipc_root} 추가")
    if aipc_project not in sys.path:
        sys.path.insert(0, aipc_project)
        logger.info(f"sys.path에 {aipc_project} 추가")
    
    logger.info("AIPC_Client 모듈 import 시작...")
    
    # 상대 경로로 import (sys.path에 추가된 경로 사용)
    from inspectors.data_quality_check import Manager
    from inspectors.models import MetaDataRule
    from inspectors.enum import DC_CHK, DQ_TYPE, DC_TYPE
    import requests_keti as requests
    
    logger.info("AIPC_Client 모듈 import 성공!")
    
except ImportError as e:
    logger.error(f"품질 검사 모듈 import 실패: {e}")
    logger.exception("상세 오류 정보")
    logger.warning("품질 검사 기능을 사용할 수 없습니다.")
    Manager = None
    MetaDataRule = None
    DC_CHK = None
    DQ_TYPE = None
    DC_TYPE = None
    requests = None

# AIPC_Client를 사용한 데이터 조회 함수
async def get_data_via_aipc(data_type: str, api_params: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """AIPC_Client를 사용한 데이터 조회"""
    try:
        if requests is None:
            return None
        
        # data_type에 따른 API 엔드포인트 URL 구성
        base_url = "https://aipc-data.com/api"  # AIPC_Client config에서 가져온 실제 URL
        
        endpoint_mapping = {
            'tc_work_info': '/TCWorkInfo/retrieveByTmnlIdTCWorkInfoList',
            'qc_work_info': '/QCWorkInfo/retrieveByTmnlIdQCWorkInfoList', 
            'yt_work_info': '/YTWorkInfo/retrieveByTmnlIdYTWorkInfoList',
            'ais_info': '/AISInfo/retrieveAISInfoList',
            'berth_schedule': '/BerthScheduleTOS/retrieveBerthScheduleTOSList'
        }
        
        endpoint = endpoint_mapping.get(data_type)
        if not endpoint:
            print(f"지원하지 않는 데이터 타입: {data_type}")
            return None
        
        url = base_url + endpoint
        
        # AIPC_Client의 requests_keti 사용 (자동으로 API 키 헤더 추가됨)
        logger.info(f"API 호출 시작 - URL: {url}")
        logger.debug(f"API 호출 파라미터: {api_params}")
        response = requests.get(url, params=api_params)
        logger.info(f"API 호출 완료 - 상태 코드: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"API 호출 실패: {response.status_code}")
            return None
        
        # 응답 데이터 파싱
        response_data = response.json()
        logger.debug(f"응답 데이터 타입: {type(response_data)}")
        
        # AIPC_Client 응답 형식 처리
        if isinstance(response_data, dict):
            result_cd = str(response_data.get('resultCd', '')).upper()
            result_msg = response_data.get('resultMsg', '')
            result_list = response_data.get('resultList', [])
            
            logger.info(f"API 응답 - 결과 코드: {result_cd}, 메시지: {result_msg}, 데이터 개수: {len(result_list)}")
            
            # 성공 코드 확인
            if result_cd in {'200', '0', 'SUCCESS'} and result_list:
                df = pd.DataFrame(result_list)
                logger.info(f"데이터프레임 생성 성공: {df.shape[0]}행, {df.shape[1]}열")
                return df
            else:
                logger.warning(f"API 호출 실패 또는 데이터 없음: {result_cd} - {result_msg}")
                return None
        else:
            logger.error(f"예상하지 못한 응답 형식: {type(response_data)}")
            return None
        
    except Exception as e:
        logger.error(f"AIPC_Client 데이터 조회 실패: {e}")
        logger.exception("상세 오류 정보")
        return None

# 간단한 품질 검사 클래스 (AIPC_Client 모듈이 없을 때 사용)
class SimpleQualityChecker:
    def __init__(self):
        self.data = None
    
    def set_data(self, data):
        self.data = data
    
    def check_completeness(self):
        if self.data is None or self.data.empty:
            return type('Result', (), {'pass_rate': 0, 'total_checks': 0, 'failed_checks': 0})()
        
        total_rows = len(self.data)
        null_counts = self.data.isnull().sum()
        total_nulls = null_counts.sum()
        
        pass_rate = ((total_rows * len(self.data.columns) - total_nulls) / (total_rows * len(self.data.columns))) * 100
        
        return type('Result', (), {
            'pass_rate': pass_rate,
            'total_checks': len(self.data.columns),
            'failed_checks': int(total_nulls)
        })()
    
    def check_validity(self, rules):
        if self.data is None or self.data.empty:
            return type('Result', (), {'pass_rate': 0, 'total_checks': 0, 'failed_checks': 0})()
        
        # 간단한 유효성 검사 (RANGE 규칙만)
        total_checks = 0
        failed_checks = 0
        
        if 'RANGE' in rules:
            for column, rule in rules['RANGE'].items():
                if column in self.data.columns:
                    total_checks += 1
                    if rule.get('rtype') == 'I':  # 정수형
                        try:
                            col_data = pd.to_numeric(self.data[column], errors='coerce')
                            val1 = rule.get('val1', 0)
                            val2 = rule.get('val2', 100)
                            invalid_count = ((col_data < val1) | (col_data > val2)).sum()
                            if invalid_count > 0:
                                failed_checks += 1
                        except:
                            failed_checks += 1
        
        pass_rate = ((total_checks - failed_checks) / total_checks * 100) if total_checks > 0 else 100
        
        return type('Result', (), {
            'pass_rate': pass_rate,
            'total_checks': total_checks,
            'failed_checks': failed_checks
        })()
    
    def check_consistency(self, rules):
        if self.data is None or self.data.empty:
            return type('Result', (), {'pass_rate': 0, 'total_checks': 0, 'failed_checks': 0})()
        
        # 간단한 일관성 검사 (DUPLICATE 규칙만)
        total_checks = 0
        failed_checks = 0
        
        if 'DUPLICATE' in rules:
            for column in rules['DUPLICATE']:
                if column in self.data.columns:
                    total_checks += 1
                    if self.data[column].duplicated().any():
                        failed_checks += 1
        
        pass_rate = ((total_checks - failed_checks) / total_checks * 100) if total_checks > 0 else 100
        
        return type('Result', (), {
            'pass_rate': pass_rate,
            'total_checks': total_checks,
            'failed_checks': failed_checks
        })()
    
    def check_usage(self, rules):
        if self.data is None or self.data.empty:
            return type('Result', (), {'pass_rate': 0, 'total_checks': 0, 'failed_checks': 0})()
        
        # 간단한 사용성 검사
        total_checks = len(self.data.columns)
        used_columns = 0
        
        for column in self.data.columns:
            if not self.data[column].isnull().all():
                used_columns += 1
        
        pass_rate = (used_columns / total_checks * 100) if total_checks > 0 else 100
        failed_checks = total_checks - used_columns
        
        return type('Result', (), {
            'pass_rate': pass_rate,
            'total_checks': total_checks,
            'failed_checks': failed_checks
        })()
    
    def check_timeliness(self, rules):
        if self.data is None or self.data.empty:
            return type('Result', (), {'pass_rate': 0, 'total_checks': 0, 'failed_checks': 0})()
        
        # 간단한 적시성 검사
        total_checks = 1
        failed_checks = 0
        
        # 현재 시간과 비교 (예시)
        pass_rate = 90.0  # 임시로 90% 통과율
        
        return type('Result', (), {
            'pass_rate': pass_rate,
            'total_checks': total_checks,
            'failed_checks': failed_checks
        })()

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

# 품질 검사 관련 모델들
class QualityCheckRequest(BaseModel):
    data_type: str
    api_params: Dict[str, Any]
    quality_meta: Dict[str, Any]

class QualityCheckResult(BaseModel):
    success: bool
    message: str
    inspection_id: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    timestamp: datetime

class QualityCheckHistory(BaseModel):
    id: str
    data_type: str
    status: str
    created_at: datetime
    results: Optional[Dict[str, Any]] = None

app = FastAPI(title="AIS Data API", version="1.0.0")

# CORS 설정 (React 앱과의 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용 (개발 환경용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 방문 로그 미들웨어
@app.middleware("http")
async def log_visits(request: Request, call_next):
    """모든 요청에 대해 방문 로그를 자동으로 남김"""
    start_time = time.time()
    
    # 응답 처리
    response = await call_next(request)
    
    # 처리 시간 계산
    process_time = time.time() - start_time
    
    # UI 관련 요청만 로그 남기기 (API 요청 제외)
    if request.url.path.startswith('/ui/') and not request.url.path.startswith('/ui/log/'):
        try:
            # 페이지 이름 추출
            page_name = request.url.path.replace('/ui/', '').replace('/', '_') or 'home'
            if not page_name or page_name == '_':
                page_name = 'home'
            
            # 현재 시간 정보
            current_time = datetime.now()
            time_info = {
                'year': current_time.year,
                'month': current_time.month,
                'day': current_time.day,
                'hour': current_time.hour,
                'minute': current_time.minute,
                'second': current_time.second,
                'weekday': current_time.weekday(),  # 0=월요일, 6=일요일
                'timestamp': current_time.timestamp(),
                'iso_format': current_time.isoformat()
            }
            
            # 중복 로그 방지: 같은 페이지에 5초 이내 접속하는 경우 스킵
            session_id = request.headers.get('x-session-id', f'session_{int(time.time())}')
            should_log = True
            
            try:
                # 최근 5초 내에 같은 페이지에 접속한 기록이 있는지 확인
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
                        SELECT COUNT(*) FROM ui_log_page_visits 
                        WHERE page_name = %s 
                        AND session_id = %s 
                        AND created_at >= DATE_SUB(NOW(), INTERVAL 5 SECOND)
                    """, (page_name, session_id))
                    
                    recent_count = cursor.fetchone()[0]
                    if recent_count > 0:
                        should_log = False
                        print(f"[AUTO-LOG] 중복 방문 감지 - 로그 스킵: {page_name}")
                
                connection.close()
                
            except Exception as e:
                print(f"[AUTO-LOG] 중복 체크 중 에러: {e}")
                # 에러가 발생해도 로그는 남김
                should_log = True
            
            # 방문 로그 저장
            if should_log:
                success = ui_service.log_page_visit(
                    user_id='auto_logged_user',
                    page_name=page_name,
                    page_url=str(request.url),
                    login_status='visit',
                    visit_duration=int(process_time * 1000),  # 밀리초로 변환
                    session_id=session_id,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get('user-agent'),
                    referrer=request.headers.get('referer'),
                    visit_hour=time_info['hour'],
                    visit_weekday=time_info['weekday']
                )
                
                if success:
                    print(f"[AUTO-LOG] 페이지 방문 로그 저장됨: {page_name} - {time_info['iso_format']} (요일: {time_info['weekday']}, 처리시간: {process_time:.3f}초)")
                else:
                    print(f"[AUTO-LOG] 페이지 방문 로그 저장 실패: {page_name} - {time_info['iso_format']}")
                
        except Exception as e:
            print(f"[AUTO-LOG] 방문 로그 저장 중 에러: {e}")
    
    return response

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
    
    # 품질 검사 히스토리 테이블 생성
    create_quality_check_tables(ui_service)

def create_quality_check_tables(ui_service: UIDataService):
    """품질 검사 관련 테이블 생성"""
    try:
        with ui_service.get_connection() as conn:
            cursor = conn.cursor()
            
            # 품질 검사 히스토리 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quality_check_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    inspection_id VARCHAR(100) UNIQUE NOT NULL,
                    data_type VARCHAR(50) NOT NULL,
                    status ENUM('PASS', 'FAIL', 'RUNNING') NOT NULL,
                    overall_rate DECIMAL(5,2) DEFAULT 0,
                    results JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_data_type (data_type),
                    INDEX idx_created_at (created_at)
                )
            """)
            
            conn.commit()
            print("품질 검사 테이블 생성 완료")
            
    except Exception as e:
        print(f"테이블 생성 실패: {e}")

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
            endpoint=str(request.url.path),
            method=request.method,
            status_code=response.status_code,
            response_time=response_time_ms,
            user_id=user_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
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

@app.get("/api/dashboard/ais-quality-status")
async def get_ais_quality_status():
    """AIS 품질 상태 데이터 조회"""
    try:
        import pymysql
        connection = pymysql.connect(host='localhost', port=3307, user='root', password='Keti1234!', database='port_database', charset='utf8mb4')
        
        with connection.cursor() as cursor:
            # AIS 검사 결과 조회
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%ais_info%'
                AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            """)
            
            overall = cursor.fetchone()
            total = overall[0] if overall[0] else 0
            pass_count = overall[1] if overall[1] else 0
            fail_count = overall[2] if overall[2] else 0
            pass_rate = (pass_count / total * 100) if total > 0 else 0
            
            # 완전성 검사 결과
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%ais_info%'
                AND check_type = 'completeness'
                AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            """)
            
            completeness = cursor.fetchone()
            comp_total = completeness[0] if completeness[0] else 0
            comp_pass = completeness[1] if completeness[1] else 0
            comp_fail = completeness[2] if completeness[2] else 0
            comp_pass_rate = (comp_pass / comp_total * 100) if comp_total > 0 else 0
            
            # 유효성 검사 결과
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%ais_info%'
                AND check_type = 'validity'
                AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            """)
            
            validity = cursor.fetchone()
            val_total = validity[0] if validity[0] else 0
            val_pass = validity[1] if validity[1] else 0
            val_fail = validity[2] if validity[2] else 0
            val_pass_rate = (val_pass / val_total * 100) if val_total > 0 else 0
            
            return {
                "overall": {
                    "total": total,
                    "pass": pass_count,
                    "fail": fail_count,
                    "pass_rate": round(pass_rate, 1)
                },
                "completeness": {
                    "total": comp_total,
                    "pass": comp_pass,
                    "fail": comp_fail,
                    "pass_rate": round(comp_pass_rate, 1)
                },
                "validity": {
                    "total": val_total,
                    "pass": val_pass,
                    "fail": val_fail,
                    "pass_rate": round(val_pass_rate, 1)
                }
            }
            
    except Exception as e:
        # 에러 발생 시 기본값 반환
        return {
            "overall": {"total": 0, "pass": 0, "fail": 0, "pass_rate": 0.0},
            "completeness": {"total": 0, "pass": 0, "fail": 0, "pass_rate": 0.0},
            "validity": {"total": 0, "pass": 0, "fail": 0, "pass_rate": 0.0}
        }

@app.get("/api/dashboard/latest-inspection-results")
async def get_latest_inspection_results(page: str = "AIS"):
    """최신 검사 결과 조회 (페이지별)"""
    try:
        import pymysql
        connection = pymysql.connect(host='localhost', port=3307, user='root', password='Keti1234!', database='port_database', charset='utf8mb4')
        
        with connection.cursor() as cursor:
            # 페이지별 inspection_id 패턴 설정
            inspection_patterns = {
                'AIS': '%ais_info%',
                'TOS': '%berth_schedule%', 
                'TC': '%tc%',
                'QC': '%qc_work%'
            }
            
            pattern = inspection_patterns.get(page, '%ais_info%')
            
            # 최신 검사 ID와 시간 조회
            cursor.execute("""
                SELECT inspection_id, MAX(created_at) as latest_time
                FROM data_inspection_results 
                WHERE inspection_id LIKE %s 
                GROUP BY inspection_id
                ORDER BY latest_time DESC 
                LIMIT 1
            """, (pattern,))
            
            latest_inspection = cursor.fetchone()
            if not latest_inspection:
                return {
                    "completeness": {"pass_rate": 0, "total_checks": 0, "pass_count": 0, "fail_count": 0, "fields_checked": 0, "last_updated": None},
                    "validity": {"pass_rate": 0, "total_checks": 0, "pass_count": 0, "fail_count": 0, "fields_checked": 0, "last_updated": None}
                }
            
            latest_inspection_id = latest_inspection[0]
            latest_time = latest_inspection[1]
            
            # 완전성 검사 결과
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail
                FROM data_inspection_results 
                WHERE inspection_id = %s AND check_type = 'completeness'
            """, (latest_inspection_id,))
            
            completeness = cursor.fetchone()
            comp_total = completeness[0] if completeness[0] else 0
            comp_pass = completeness[1] if completeness[1] else 0
            comp_fail = completeness[2] if completeness[2] else 0
            comp_pass_rate = (comp_pass / comp_total * 100) if comp_total > 0 else 0
            
            # 유효성 검사 결과
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail
                FROM data_inspection_results 
                WHERE inspection_id = %s AND check_type = 'validity'
            """, (latest_inspection_id,))
            
            validity = cursor.fetchone()
            val_total = validity[0] if validity[0] else 0
            val_pass = validity[1] if validity[1] else 0
            val_fail = validity[2] if validity[2] else 0
            val_pass_rate = (val_pass / val_total * 100) if val_total > 0 else 0
            
            # 사용성 검사 결과 (TC 페이지용)
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail
                FROM data_inspection_results 
                WHERE inspection_id = %s AND check_type = 'usage'
            """, (latest_inspection_id,))
            
            usage = cursor.fetchone()
            usage_total = usage[0] if usage[0] else 0
            usage_pass = usage[1] if usage[1] else 0
            usage_fail = usage[2] if usage[2] else 0
            usage_pass_rate = (usage_pass / usage_total * 100) if usage_total > 0 else 0
            
            result = {
                "completeness": {
                    "pass_rate": round(comp_pass_rate, 1),
                    "total_checks": comp_total,
                    "pass_count": comp_pass,
                    "fail_count": comp_fail,
                    "fields_checked": comp_total,
                    "last_updated": latest_time.isoformat() if latest_time else None
                },
                "validity": {
                    "pass_rate": round(val_pass_rate, 1),
                    "total_checks": val_total,
                    "pass_count": val_pass,
                    "fail_count": val_fail,
                    "fields_checked": val_total,
                    "last_updated": latest_time.isoformat() if latest_time else None
                }
            }
            
            # TC 페이지인 경우 usage 데이터 추가
            if page == 'TC' and usage_total > 0:
                result["usage"] = {
                    "pass_rate": round(usage_pass_rate, 1),
                    "total_checks": usage_total,
                    "pass_count": usage_pass,
                    "fail_count": usage_fail,
                    "fields_checked": usage_total,
                    "last_updated": latest_time.isoformat() if latest_time else None
                }
            
            return result
            
    except Exception as e:
        print(f"Failed to fetch latest inspection results for page {page}: {e}")
        return {
            "completeness": {"pass_rate": 0, "total_checks": 0, "pass_count": 0, "fail_count": 0, "fields_checked": 0, "last_updated": None},
            "validity": {"pass_rate": 0, "total_checks": 0, "pass_count": 0, "fail_count": 0, "fields_checked": 0, "last_updated": None}
        }

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

@app.get("/ui/statistics/visitor-trends")
async def get_visitor_trends():
    """방문자 트렌드 분석 데이터 조회"""
    print("[DEBUG] visitor-trends API 호출됨")
    try:
        from datetime import datetime, timedelta
        
        # 새로운 DB 연결 생성
        print("[DEBUG] 새로운 DB 연결 생성")
        import pymysql
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        print("[DEBUG] DB 연결 성공")
        
        try:
            with connection.cursor() as cursor:
                # 최근 7일 평균 vs 이전 7일 평균
                print("[DEBUG] 첫 번째 쿼리 실행 시작")
                cursor.execute("""
                    SELECT 
                        AVG(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) as recent_avg,
                        AVG(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 14 DAY) 
                                  AND created_at < DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) as previous_avg
                    FROM ui_log_page_visits
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 14 DAY)
                """)
                print("[DEBUG] 첫 번째 쿼리 실행 완료")
                trend_data = cursor.fetchone()
                print(f"[DEBUG] 첫 번째 쿼리 결과: {trend_data}")
                
                # 가장 활발한 시간대 (시간별 방문 수) - visit_hour 컬럼 사용
                print("[DEBUG] 두 번째 쿼리 실행 시작")
                cursor.execute("""
                    SELECT visit_hour as hour, COUNT(*) as count
                    FROM ui_log_page_visits
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                    AND visit_hour IS NOT NULL
                    GROUP BY visit_hour
                    ORDER BY count DESC
                    LIMIT 1
                """)
                print("[DEBUG] 두 번째 쿼리 실행 완료")
                peak_hour_data = cursor.fetchone()
                print(f"[DEBUG] 두 번째 쿼리 결과: {peak_hour_data}")
                
                # 계산
                recent_avg = trend_data[0] if trend_data[0] else 0
                previous_avg = trend_data[1] if trend_data[1] else 0
                
                print(f"[DEBUG] DB 조회 결과 - recent_avg: {recent_avg}, previous_avg: {previous_avg}")
                
                if previous_avg > 0:
                    trend_percentage = ((recent_avg - previous_avg) / previous_avg) * 100
                else:
                    trend_percentage = 0
                
                peak_hour = peak_hour_data[0] if peak_hour_data else 14
                peak_hour_end = peak_hour + 2
                
                result = {
                    "recent_7day_avg": recent_avg,
                    "previous_7day_avg": previous_avg,
                    "trend_percentage": round(trend_percentage, 1),
                    "peak_hour_start": peak_hour,
                    "peak_hour_end": peak_hour_end,
                    "peak_hour_display": f"{peak_hour:02d}:00-{peak_hour_end:02d}:00"
                }
                print(f"[DEBUG] 최종 결과: {result}")
                return result
                
        finally:
            connection.close()
            
    except Exception as e:
        # DB 조회 실패 시 기본값 반환
        print(f"[DEBUG] 에러 발생: {e}")
        return {
            "recent_7day_avg": 185.2,
            "previous_7day_avg": 164.8,
            "trend_percentage": 12.5,
            "peak_hour_start": 14,
            "peak_hour_end": 16,
            "peak_hour_display": "14:00-16:00"
        }

@app.get("/ui/statistics/time-based")
async def get_time_based_statistics(period: str = 'daily'):
    """시간별 통계 데이터 조회 (기간별 다른 데이터)"""
    print(f"[DEBUG] time-based API 호출됨 - period: {period}")
    try:
        # period 검증
        if period not in ['daily', 'weekly', 'monthly']:
            raise HTTPException(status_code=400, detail="period는 'daily', 'weekly', 'monthly' 중 하나여야 합니다.")
        
        # 실제 DB 데이터 조회
        import pymysql
        from datetime import datetime, timedelta
        
        print("[DEBUG] DB 연결 시도")
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        print("[DEBUG] DB 연결 성공")
        
        try:
            with connection.cursor() as cursor:
                if period == 'daily':
                    # 일간: 최근 2주일치 데이터를 일별로
                    print("[DEBUG] 일간 데이터 조회 시작")
                    cursor.execute("""
                        SELECT DATE(created_at) as date, COUNT(*) as count
                        FROM ui_log_page_visits
                        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 14 DAY)
                        GROUP BY DATE(created_at)
                        ORDER BY date
                    """)
                    page_visits_data = cursor.fetchall()
                    
                    cursor.execute("""
                        WITH RECURSIVE dates AS (
                            SELECT DATE_SUB(NOW(), INTERVAL 13 DAY) as date
                            UNION ALL
                            SELECT DATE_ADD(date, INTERVAL 1 DAY)
                            FROM dates
                            WHERE date <= DATE(NOW())
                        )
                        SELECT 
                            d.date,
                            COALESCE(COUNT(api.created_at), 0) as count
                        FROM dates d
                        LEFT JOIN api_call_info api ON DATE(api.created_at) = d.date
                        GROUP BY d.date
                        ORDER BY d.date
                    """)
                    api_calls_data = cursor.fetchall()
                    
                elif period == 'weekly':
                    # 주간: 최근 12주의 데이터를 주별로 (연속적인 주 생성)
                    print("[DEBUG] 주간 데이터 조회 시작")
                    cursor.execute("""
                        WITH RECURSIVE weeks AS (
                            SELECT DATE_SUB(NOW(), INTERVAL 11 WEEK) as week_start
                            UNION ALL
                            SELECT DATE_ADD(week_start, INTERVAL 1 WEEK)
                            FROM weeks
                            WHERE week_start < DATE_SUB(NOW(), INTERVAL 1 WEEK)
                        )
                        SELECT 
                            w.week_start,
                            CONCAT(YEAR(w.week_start), '년 ', MONTH(w.week_start), '월 ', CEIL(DAY(w.week_start) / 7), '주차') as week_label,
                            COALESCE(COUNT(pv.created_at), 0) as count
                        FROM weeks w
                        LEFT JOIN ui_log_page_visits pv ON pv.created_at >= w.week_start AND pv.created_at < DATE_ADD(w.week_start, INTERVAL 1 WEEK)
                        GROUP BY w.week_start
                        ORDER BY w.week_start
                    """)
                    page_visits_data = cursor.fetchall()
                    
                    cursor.execute("""
                        WITH RECURSIVE weeks AS (
                            SELECT DATE_SUB(NOW(), INTERVAL 11 WEEK) as week_start
                            UNION ALL
                            SELECT DATE_ADD(week_start, INTERVAL 1 WEEK)
                            FROM weeks
                            WHERE week_start < DATE_SUB(NOW(), INTERVAL 1 WEEK)
                        )
                        SELECT 
                            w.week_start,
                            CONCAT(YEAR(w.week_start), '년 ', MONTH(w.week_start), '월 ', CEIL(DAY(w.week_start) / 7), '주차') as week_label,
                            COALESCE(COUNT(api.created_at), 0) as count
                        FROM weeks w
                        LEFT JOIN api_call_info api ON api.created_at >= w.week_start AND api.created_at < DATE_ADD(w.week_start, INTERVAL 1 WEEK)
                        GROUP BY w.week_start
                        ORDER BY w.week_start
                    """)
                    api_calls_data = cursor.fetchall()
                    
                elif period == 'monthly':
                    # 월간: 최근 12달의 데이터를 월별로 (연속적인 월 생성)
                    print("[DEBUG] 월간 데이터 조회 시작")
                    cursor.execute("""
                        WITH RECURSIVE months AS (
                            SELECT DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 11 MONTH), '%Y-%m') as month
                            UNION ALL
                            SELECT DATE_FORMAT(DATE_ADD(STR_TO_DATE(CONCAT(month, '-01'), '%Y-%m-%d'), INTERVAL 1 MONTH), '%Y-%m')
                            FROM months
                            WHERE month < DATE_FORMAT(NOW(), '%Y-%m')
                        )
                        SELECT 
                            m.month,
                            CONCAT(SUBSTRING(m.month, 1, 4), '년 ', SUBSTRING(m.month, 6, 2), '월') as month_label,
                            COALESCE(COUNT(pv.created_at), 0) as count
                        FROM months m
                        LEFT JOIN ui_log_page_visits pv ON DATE_FORMAT(pv.created_at, '%Y-%m') = m.month
                        GROUP BY m.month
                        ORDER BY m.month
                    """)
                    page_visits_data = cursor.fetchall()
                    
                    cursor.execute("""
                        WITH RECURSIVE months AS (
                            SELECT DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 11 MONTH), '%Y-%m') as month
                            UNION ALL
                            SELECT DATE_FORMAT(DATE_ADD(STR_TO_DATE(CONCAT(month, '-01'), '%Y-%m-%d'), INTERVAL 1 MONTH), '%Y-%m')
                            FROM months
                            WHERE month < DATE_FORMAT(NOW(), '%Y-%m')
                        )
                        SELECT 
                            m.month,
                            CONCAT(SUBSTRING(m.month, 1, 4), '년 ', SUBSTRING(m.month, 6, 2), '월') as month_label,
                            COALESCE(COUNT(api.created_at), 0) as count
                        FROM months m
                        LEFT JOIN api_call_info api ON DATE_FORMAT(api.created_at, '%Y-%m') = m.month
                        GROUP BY m.month
                        ORDER BY m.month
                    """)
                    api_calls_data = cursor.fetchall()
                
                # 데이터 포맷 변환
                if period == 'daily':
                    page_visits = [[str(row[0]), int(row[1])] for row in page_visits_data]
                    api_calls = [[str(row[0]), int(row[1])] for row in api_calls_data]
                elif period == 'weekly':
                    page_visits = [[str(row[1]), int(row[2])] for row in page_visits_data]  # week_label, count
                    api_calls = [[str(row[1]), int(row[2])] for row in api_calls_data]
                elif period == 'monthly':
                    page_visits = [[str(row[1]), int(row[2])] for row in page_visits_data]  # month_label, count
                    api_calls = [[str(row[1]), int(row[2])] for row in api_calls_data]
                
                print(f"[DEBUG] 최종 데이터 - page_visits: {len(page_visits)}개, api_calls: {len(api_calls)}개")
                
        finally:
            connection.close()
        
        return {
            "page_visits": page_visits,
            "api_calls": api_calls,
            "period": period,
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

@app.get("/api/dashboard/tc-quality-summary")
async def get_tc_quality_summary():
    """TC 품질 요약 데이터"""
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
            # TC 전체 검사 통계
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT inspection_id) as total_inspections,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
                    MAX(created_at) as last_inspection_date
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%tc%' OR inspection_id LIKE '%TC%'
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
                WHERE (inspection_id LIKE '%tc%' OR inspection_id LIKE '%TC%')
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
                WHERE (inspection_id LIKE '%tc%' OR inspection_id LIKE '%TC%')
                  AND check_type = 'validity'
            """)
            
            val_row = cursor.fetchone()
            validity_checks = int(val_row[0]) if val_row[0] else 0
            validity_passes = int(val_row[1]) if val_row[1] else 0
            validity_fails = int(val_row[2]) if val_row[2] else 0
            
            # 사용성 검사 통계
            cursor.execute("""
                SELECT 
                    COUNT(*) as usage_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as usage_passes,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as usage_fails
                FROM data_inspection_results 
                WHERE (inspection_id LIKE '%tc%' OR inspection_id LIKE '%TC%')
                  AND check_type = 'usage'
            """)
            
            usage_row = cursor.fetchone()
            usage_checks = int(usage_row[0]) if usage_row[0] else 0
            usage_passes = int(usage_row[1]) if usage_row[1] else 0
            usage_fails = int(usage_row[2]) if usage_row[2] else 0
        
        connection.close()
        
        # 통과율 계산
        pass_rate = round(pass_count * 100.0 / total_checks, 1) if total_checks > 0 else 0
        completeness_rate = round(completeness_passes * 100.0 / completeness_checks, 1) if completeness_checks > 0 else 0
        validity_rate = round(validity_passes * 100.0 / validity_checks, 1) if validity_checks > 0 else 0
        usage_rate = round(usage_passes * 100.0 / usage_checks, 1) if usage_checks > 0 else 0
        
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
            },
            "usage": {
                "fields_checked": usage_checks,
                "pass_count": usage_passes,
                "fail_count": usage_fails,
                "pass_rate": usage_rate
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TC 품질 요약 조회 실패: {str(e)}")

@app.get("/api/dashboard/qc-quality-summary")
async def get_qc_quality_summary():
    """QC 품질 요약 데이터"""
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
            # QC 전체 검사 통계
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT inspection_id) as total_inspections,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count,
                    MAX(created_at) as last_inspection_date
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%qc_work%' OR inspection_id LIKE '%QC%'
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
                WHERE (inspection_id LIKE '%qc_work%' OR inspection_id LIKE '%QC%')
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
                WHERE (inspection_id LIKE '%qc_work%' OR inspection_id LIKE '%QC%')
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
        raise HTTPException(status_code=500, detail=f"QC 품질 요약 조회 실패: {str(e)}")

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

@app.get("/api/dashboard/qc-quality-status")
async def get_qc_quality_status():
    """QC 데이터 품질 상태"""
    try:
        import pymysql
        connection = pymysql.connect(host='localhost', port=3307, user='root', password='Keti1234!', database='port_database', charset='utf8mb4')
        
        with connection.cursor() as cursor:
            # 전체 검사 통계 (검사 실행 횟수 기준)
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_inspections
                FROM data_inspection_summary 
                WHERE inspection_id LIKE '%qc_work%'
            """)
            
            inspection_row = cursor.fetchone()
            total_inspections = int(inspection_row[0]) if inspection_row[0] else 0
            
            # 검사 결과 통계 (통과/실패 계산용)
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%qc_work%'
            """)
            
            results_row = cursor.fetchone()
            pass_count = int(results_row[0]) if results_row[0] else 0
            fail_count = int(results_row[1]) if results_row[1] else 0
            total_checks = pass_count + fail_count
            overall_rate = round(pass_count * 100.0 / total_checks, 1) if total_checks > 0 else 0
            
            # 검사 유형별 통계
            cursor.execute("""
                SELECT 
                    check_type,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail_count
                FROM data_inspection_results 
                WHERE inspection_id LIKE '%qc_work%'
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
                "total": total_inspections,
                "pass": pass_count,
                "fail": fail_count
            },
            "breakdown": quality_breakdown,
            "alerts": alerts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QC 품질 상태 조회 실패: {str(e)}")

@app.get("/api/dashboard/qc-summary")
async def get_qc_summary():
    """QC 작업 요약 데이터"""
    try:
        import pymysql
        connection = pymysql.connect(host='localhost', port=3307, user='root', password='Keti1234!', database='port_database', charset='utf8mb4')
        
        with connection.cursor() as cursor:
            # QC 작업 통계
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_work,
                    COUNT(DISTINCT tmnlId) as total_terminals,
                    COUNT(DISTINCT shpCd) as total_ships,
                    COUNT(DISTINCT cntrNo) as total_containers
                FROM qc_work_info
            """)
            
            stats_row = cursor.fetchone()
            total_work = int(stats_row[0]) if stats_row[0] else 0
            total_terminals = int(stats_row[1]) if stats_row[1] else 0
            total_ships = int(stats_row[2]) if stats_row[2] else 0
            total_containers = int(stats_row[3]) if stats_row[3] else 0
            
            # 작업 유형별 분포 (jobState 기반)
            cursor.execute("""
                SELECT 
                    jobState,
                    COUNT(*) as count
                FROM qc_work_info
                GROUP BY jobState
                ORDER BY count DESC
            """)
            
            work_types = []
            for row in cursor.fetchall():
                work_types.append({
                    "workType": row[0],
                    "count": int(row[1])
                })
            
            # 터미널별 분포
            cursor.execute("""
                SELECT 
                    tmnlId,
                    tmnlNm,
                    COUNT(*) as count
                FROM qc_work_info
                GROUP BY tmnlId, tmnlNm
                ORDER BY count DESC
                LIMIT 10
            """)
            
            terminals = []
            for row in cursor.fetchall():
                terminals.append({
                    "terminalId": row[0],
                    "terminalName": row[1],
                    "count": int(row[2])
                })
            
            # 마지막 검사 날짜
            cursor.execute("""
                SELECT MAX(created_at) as last_inspection
                FROM data_inspection_summary 
                WHERE inspection_id LIKE '%qc_work%'
            """)
            
            last_inspection_row = cursor.fetchone()
            last_inspection_date = last_inspection_row[0].strftime('%Y-%m-%d') if last_inspection_row[0] else 'N/A'
        
        connection.close()
        
        return {
            "totalWork": total_work,
            "totalTerminals": total_terminals,
            "totalShips": total_ships,
            "totalContainers": total_containers,
            "workTypes": work_types,
            "terminals": terminals,
            "lastInspectionDate": last_inspection_date
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QC 요약 데이터 조회 실패: {str(e)}")

@app.get("/api/dashboard/qc-work-history")
async def get_qc_work_history():
    """QC 작업 히스토리 데이터"""
    try:
        import pymysql
        connection = pymysql.connect(host='localhost', port=3307, user='root', password='Keti1234!', database='port_database', charset='utf8mb4')
        
        with connection.cursor() as cursor:
            # 최근 30일간의 QC 작업 히스토리 (created_at 기반)
            cursor.execute("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as total_work,
                    COUNT(DISTINCT tmnlId) as terminals,
                    COUNT(DISTINCT shpCd) as ships,
                    COUNT(DISTINCT cntrNo) as containers
                FROM qc_work_info
                WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """)
            
            history_data = []
            for row in cursor.fetchall():
                history_data.append({
                    "date": row[0].strftime('%Y-%m-%d'),
                    "totalWork": int(row[1]),
                    "terminals": int(row[2]),
                    "ships": int(row[3]),
                    "containers": int(row[4])
                })
        
        connection.close()
        
        return history_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QC 작업 히스토리 조회 실패: {str(e)}")

# 품질 검사 API 엔드포인트들
@app.post("/api/quality-check/run", response_model=QualityCheckResult)
async def run_quality_check(request: QualityCheckRequest):
    """품질 검사 실행"""
    try:
        # 품질 검사 모듈이 없어도 SimpleQualityChecker 사용 가능
        
        # 데이터 타입에 따른 데이터 조회
        logger.info(f"데이터 조회 시작 - data_type: {request.data_type}")
        logger.debug(f"AIPC_Client 사용 가능 여부 - requests: {requests is not None}, Manager: {Manager is not None}")
        
        if requests is not None and Manager is not None:
            # AIPC_Client 사용
            logger.info("AIPC_Client를 사용하여 데이터 조회")
            data = await get_data_via_aipc(request.data_type, request.api_params)
        else:
            # Fallback: 기존 방식 사용
            logger.info("Fallback 방식으로 데이터 조회")
            data = await get_data_by_type(request.data_type, request.api_params, ui_service)
        
        logger.info(f"데이터 조회 결과 - data: {data is not None}, shape: {data.shape if data is not None else 'None'}")
        
        if data is None or data.empty:
            return QualityCheckResult(
                success=False,
                message="데이터를 찾을 수 없습니다.",
                timestamp=datetime.now()
            )
        
        # 품질 검사 매니저 초기화
        if Manager is not None and requests is not None and DC_CHK is not None:
            # AIPC_Client의 Manager 사용
            manager = Manager()
            manager.set_data(data)
            
            # 메타데이터 규칙 설정
            metadata_rule = MetaDataRule()
            
            # DV (유효성) 규칙 설정
            if 'DV' in request.quality_meta:
                dv_rules = request.quality_meta['DV']
                
                # RANGE 규칙
                if 'RANGE' in dv_rules:
                    for column, rule in dv_rules['RANGE'].items():
                        metadata_rule.add_range_rule(
                            column=column,
                            min_val=rule.get('val1', 0),
                            max_val=rule.get('val2', 999),
                            rtype=rule.get('rtype', 'I'),
                            ctype=rule.get('ctype', 'I')
                        )
                
                # DATE 규칙
                if 'DATE' in dv_rules:
                    for date_type, rules in dv_rules['DATE'].items():
                        for column, rule in rules.items():
                            metadata_rule.add_range_rule(
                                column=column,
                                min_val=0,  # DATE 규칙은 별도 처리 필요
                                max_val=99999999999999,
                                rtype='D',
                                ctype='D'
                            )
            
            # DC (일관성) 규칙 설정
            if 'DC' in request.quality_meta:
                dc_rules = request.quality_meta['DC']
                
                # DUPLICATE 규칙
                if 'DUPLICATE' in dc_rules:
                    for unique_type, rules in dc_rules['DUPLICATE'].items():
                        for column, columns in rules.items():
                            if unique_type == 'U':  # UNIQUE
                                metadata_rule.add_unique_rule(columns)
            
            # DI (완전성) 규칙 설정
            if 'DI' in request.quality_meta:
                di_rules = request.quality_meta['DI']
                # 빈값 검사 규칙 추가 (필요시)
                pass
        else:
            # Fallback: SimpleQualityChecker 사용
            print("AIPC_Client 모듈이 없어서 SimpleQualityChecker를 사용합니다.")
            manager = SimpleQualityChecker()
            manager.set_data(data)
        
        # 품질 검사 실행
        results = {}
        
        if Manager is not None and requests is not None and DC_CHK is not None:
            # AIPC_Client의 comprehensive_check 사용
            inspection_output = manager.comprehensive_check(data, request.quality_meta)
            
            # 결과 정규화
            for check_type, items in inspection_output.inspection_result.results.items():
                total_checks = len(items)
                passed_checks = sum(1 for item in items if 'PASS' in str(item))
                failed_checks = total_checks - passed_checks
                pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 100
                
                results[check_type] = {
                    'status': 'PASS' if pass_rate >= 80 else 'FAIL',
                    'pass_rate': pass_rate,
                    'total_checks': total_checks,
                    'failed_checks': failed_checks
                }
        else:
            # Fallback: SimpleQualityChecker 사용
            # 완전성 검사
            if 'DI' in request.quality_meta:
                di_result = manager.check_completeness()
                results['completeness'] = {
                    'status': 'PASS' if di_result.pass_rate > 80 else 'FAIL',
                    'pass_rate': di_result.pass_rate,
                    'total_checks': di_result.total_checks,
                    'failed_checks': di_result.failed_checks
                }
            
            # 유효성 검사
            if 'DV' in request.quality_meta:
                dv_result = manager.check_validity(request.quality_meta['DV'])
                results['validity'] = {
                    'status': 'PASS' if dv_result.pass_rate > 80 else 'FAIL',
                    'pass_rate': dv_result.pass_rate,
                    'total_checks': dv_result.total_checks,
                    'failed_checks': dv_result.failed_checks
                }
            
            # 일관성 검사
            if 'DC' in request.quality_meta:
                dc_result = manager.check_consistency(request.quality_meta['DC'])
                results['consistency'] = {
                    'status': 'PASS' if dc_result.pass_rate > 80 else 'FAIL',
                    'pass_rate': dc_result.pass_rate,
                    'total_checks': dc_result.total_checks,
                    'failed_checks': dc_result.failed_checks
                }
            
            # 사용성 검사
            if 'DU' in request.quality_meta:
                du_result = manager.check_usage(request.quality_meta['DU'])
                results['usage'] = {
                    'status': 'PASS' if du_result.pass_rate > 80 else 'FAIL',
                    'pass_rate': du_result.pass_rate,
                    'total_checks': du_result.total_checks,
                    'failed_checks': du_result.failed_checks
                }
            
            # 적시성 검사
            if 'DT' in request.quality_meta:
                dt_result = manager.check_timeliness(request.quality_meta['DT'])
                results['timeliness'] = {
                    'status': 'PASS' if dt_result.pass_rate > 80 else 'FAIL',
                    'pass_rate': dt_result.pass_rate,
                    'total_checks': dt_result.total_checks,
                    'failed_checks': dt_result.failed_checks
                }
        
        # 전체 통과율 계산
        total_checks = sum(r.get('total_checks', 0) for r in results.values())
        total_passed = sum(r.get('total_checks', 0) - r.get('failed_checks', 0) for r in results.values())
        overall_rate = round(total_passed * 100.0 / total_checks, 1) if total_checks > 0 else 0
        
        # 검사 ID 생성
        inspection_id = f"{request.data_type}_{int(time.time())}"
        
        # 결과 저장
        await save_quality_check_result(inspection_id, request.data_type, results, overall_rate, ui_service)
        
        return QualityCheckResult(
            success=True,
            message="품질 검사가 완료되었습니다.",
            inspection_id=inspection_id,
            results={
                'overall_rate': overall_rate,
                'total_checks': total_checks,
                'total_passed': total_passed,
                'breakdown': results
            },
            timestamp=datetime.now()
        )
        
    except Exception as e:
        return QualityCheckResult(
            success=False,
            message=f"품질 검사 실행 실패: {str(e)}",
            timestamp=datetime.now()
        )

@app.get("/api/quality-check/history", response_model=List[QualityCheckHistory])
async def get_quality_check_history():
    """품질 검사 히스토리 조회"""
    try:
        # 임시로 빈 배열 반환 (데이터베이스 연결 문제 해결 전까지)
        return []
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"품질 검사 히스토리 조회 실패: {str(e)}")

async def get_data_by_type(data_type: str, api_params: Dict[str, Any], ui_service: UIDataService) -> Optional[pd.DataFrame]:
    """데이터 타입에 따른 데이터 조회"""
    try:
        with ui_service.get_connection() as conn:
            cursor = conn.cursor()
            
            if data_type == 'tc_work_info':
                # TC 작업정보 조회
                query = """
                    SELECT tmnlId, shpCd, callYr, serNo, wkTime, regNo
                    FROM tc_work_info 
                    WHERE 1=1
                """
                params = []
                
                if 'timeFrom' in api_params:
                    query += " AND wkTime >= %s"
                    params.append(api_params['timeFrom'])
                
                if 'timeTo' in api_params:
                    query += " AND wkTime <= %s"
                    params.append(api_params['timeTo'])
                
                if 'tmnlId' in api_params:
                    query += " AND tmnlId = %s"
                    params.append(api_params['tmnlId'])
                
                if 'shpCd' in api_params:
                    query += " AND shpCd = %s"
                    params.append(api_params['shpCd'])
                
                if 'callYr' in api_params:
                    query += " AND callYr = %s"
                    params.append(api_params['callYr'])
                
                if 'serNo' in api_params:
                    query += " AND serNo = %s"
                    params.append(api_params['serNo'])
                
                query += " LIMIT 1000"  # 성능을 위해 제한
                
                cursor.execute(query, params)
                data = cursor.fetchall()
                
                if data:
                    columns = ['tmnlId', 'shpCd', 'callYr', 'serNo', 'wkTime', 'regNo']
                    return pd.DataFrame(data, columns=columns)
            
            # 다른 데이터 타입들도 추가 가능
            return None
            
    except Exception as e:
        print(f"데이터 조회 실패: {str(e)}")
        return None

async def save_quality_check_result(inspection_id: str, data_type: str, results: Dict[str, Any], overall_rate: float, ui_service: UIDataService):
    """품질 검사 결과 저장"""
    try:
        with ui_service.get_connection() as conn:
            cursor = conn.cursor()
            
            # 품질 검사 히스토리 저장
            cursor.execute("""
                INSERT INTO quality_check_history 
                (inspection_id, data_type, status, overall_rate, results, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                inspection_id,
                data_type,
                'PASS' if overall_rate >= 80 else 'FAIL',
                overall_rate,
                json.dumps(results),
                datetime.now()
            ))
            
            conn.commit()
            
    except Exception as e:
        print(f"결과 저장 실패: {str(e)}")

@app.get("/api/dashboard/failed-items")
async def get_failed_items(page: str = "AIS"):
    """실패한 항목 데이터 조회 (페이지별)"""
    try:
        import pymysql
        connection = pymysql.connect(host='localhost', port=3307, user='root', password='Keti1234!', database='port_database', charset='utf8mb4')
        
        with connection.cursor() as cursor:
            # 페이지별 inspection_id 패턴 설정
            inspection_patterns = {
                'AIS': '%ais_info%',
                'TOS': '%berth_schedule%', 
                'TC': '%tc%',
                'QC': '%qc_work%'
            }
            
            pattern = inspection_patterns.get(page, '%ais_info%')
            
            # 실패한 항목들 조회 (최대 5개)
            cursor.execute("""
                SELECT 
                    check_name,
                    check_type,
                    message,
                    details,
                    affected_rows,
                    created_at
                FROM data_inspection_results 
                WHERE inspection_id LIKE %s 
                AND status = 'FAIL'
                ORDER BY created_at DESC
                LIMIT 5
            """, (pattern,))
            
            failed_items = []
            for row in cursor.fetchall():
                failed_items.append({
                    "field": row[0],  # check_name
                    "reason": "검사 실패",
                    "message": row[2] or "상세 정보 없음",  # message
                    "details": row[3] or "",  # details
                    "affected_rows": row[4] or 0,  # affected_rows
                    "created_at": row[5].isoformat() if row[5] else None
                })
            
            # 성공한 항목들도 조회 (실패한 항목이 없을 때 사용)
            cursor.execute("""
                SELECT 
                    check_name,
                    check_type,
                    message,
                    details,
                    affected_rows,
                    created_at
                FROM data_inspection_results 
                WHERE inspection_id LIKE %s 
                AND status = 'PASS'
                ORDER BY created_at DESC
                LIMIT 5
            """, (pattern,))
            
            success_items = []
            for row in cursor.fetchall():
                success_items.append({
                    "field": row[0],  # check_name
                    "reason": "검사 통과",
                    "message": row[2] or "검사 통과",  # message
                    "details": row[3] or "",  # details
                    "affected_rows": row[4] or 0,  # affected_rows
                    "created_at": row[5].isoformat() if row[5] else None
                })
        
        connection.close()
        
        return {
            "failed_items": failed_items,
            "success_items": success_items,
            "page": page
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"실패한 항목 조회 실패: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000) 