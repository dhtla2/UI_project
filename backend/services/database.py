"""Database connection and basic services"""

import pymysql
import sqlite3
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """데이터베이스 연결 및 기본 서비스"""
    
    def __init__(self):
        self.mysql_config = {
            'host': settings.db_host,
            'port': settings.db_port,
            'user': settings.db_user,
            'password': settings.db_password,
            'database': settings.db_name,
            'charset': settings.db_charset
        }
        self.ais_db_path = settings.ais_db_path
    
    @contextmanager
    def get_mysql_connection(self):
        """MySQL 연결 컨텍스트 매니저"""
        connection = None
        try:
            connection = pymysql.connect(**self.mysql_config)
            yield connection
        except Exception as e:
            logger.error(f"MySQL 연결 실패: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
    
    @contextmanager
    def get_ais_connection(self):
        """AIS SQLite 연결 컨텍스트 매니저"""
        connection = None
        try:
            connection = sqlite3.connect(self.ais_db_path)
            connection.row_factory = sqlite3.Row
            yield connection
        except Exception as e:
            logger.error(f"AIS 데이터베이스 연결 실패: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
    
    def execute_query(self, query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = True) -> Optional[Any]:
        """MySQL 쿼리 실행"""
        try:
            with self.get_mysql_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    if fetch_one:
                        return cursor.fetchone()
                    elif fetch_all:
                        return cursor.fetchall()
                    else:
                        conn.commit()
                        return cursor.rowcount
        except Exception as e:
            logger.error(f"쿼리 실행 실패: {e}")
            raise
    
    def execute_ais_query(self, query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = True) -> Optional[Any]:
        """AIS SQLite 쿼리 실행"""
        try:
            with self.get_ais_connection() as conn:
                cursor = conn.cursor()
                if params is not None:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"AIS 쿼리 실행 실패: {e}")
            raise

class UIDataService:
    """UI 데이터 서비스 (기존 ui_data_service.py 기능 통합)"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
    
    def log_page_visit(self, user_id: str, page_name: str, page_url: str, 
                      login_status: str, visit_duration: int, session_id: str = None,
                      ip_address: str = None, user_agent: str = None, referrer: str = None,
                      visit_hour: int = None, visit_weekday: int = None) -> bool:
        """페이지 방문 로그 저장"""
        try:
            query = """
                INSERT INTO ui_log_page_visits 
                (user_id, page_name, page_url, login_status, visit_duration, 
                 session_id, ip_address, user_agent, referrer, visit_hour, visit_weekday)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (user_id, page_name, page_url, login_status, visit_duration,
                     session_id, ip_address, user_agent, referrer, visit_hour, visit_weekday)
            
            self.db_service.execute_query(query, params, fetch_all=False)
            return True
        except Exception as e:
            logger.error(f"페이지 방문 로그 저장 실패: {e}")
            return False
    
    def log_api_call(self, endpoint: str, method: str, status_code: int, 
                    response_time: int, user_id: str = None, ip_address: str = None,
                    user_agent: str = None) -> bool:
        """API 호출 로그 저장"""
        try:
            query = """
                INSERT INTO api_call_info 
                (api_endpoint, request_params, response_status_code, response_time_ms, 
                 data_retrieval_start_time, created_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """
            params = (endpoint, f'{{"method": "{method}"}}', status_code, response_time)
            
            self.db_service.execute_query(query, params, fetch_all=False)
            return True
        except Exception as e:
            logger.error(f"API 호출 로그 저장 실패: {e}")
            return False

class AISService:
    """AIS 데이터 서비스 (기존 ais_service.py 기능 통합)"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
    
    def load_all_data(self, limit: int = None) -> List[Dict[str, Any]]:
        """모든 AIS 데이터 로드"""
        try:
            query = "SELECT * FROM ais_info"
            if limit:
                query += f" LIMIT {limit}"
            
            rows = self.db_service.execute_ais_query(query)
            return [dict(row) for row in rows] if rows else []
        except Exception as e:
            logger.error(f"AIS 데이터 로드 실패: {e}")
            return []
    
    def load_by_mmsi(self, mmsi: str) -> List[Dict[str, Any]]:
        """MMSI로 AIS 데이터 검색"""
        try:
            query = "SELECT * FROM ais_info WHERE mmsiNo = ?"
            rows = self.db_service.execute_ais_query(query, (mmsi,))
            return [dict(row) for row in rows] if rows else []
        except Exception as e:
            logger.error(f"MMSI 검색 실패: {e}")
            return []
    
    def load_by_ship_name(self, name: str) -> List[Dict[str, Any]]:
        """선박명으로 AIS 데이터 검색"""
        try:
            query = "SELECT * FROM ais_info WHERE vsslNm LIKE ?"
            rows = self.db_service.execute_ais_query(query, (f"%{name}%",))
            return [dict(row) for row in rows] if rows else []
        except Exception as e:
            logger.error(f"선박명 검색 실패: {e}")
            return []
    
    def load_by_flag(self, flag: str) -> List[Dict[str, Any]]:
        """국적별 AIS 데이터 검색"""
        try:
            query = "SELECT * FROM ais_info WHERE flag = ?"
            rows = self.db_service.execute_ais_query(query, (flag,))
            return [dict(row) for row in rows] if rows else []
        except Exception as e:
            logger.error(f"국적별 검색 실패: {e}")
            return []
    
    def filter_by_ship_type(self, ship_type: str) -> List[Dict[str, Any]]:
        """선박 타입별 AIS 데이터 필터링"""
        try:
            query = "SELECT * FROM ais_info WHERE vsslTp = ?"
            rows = self.db_service.execute_ais_query(query, (ship_type,))
            return [dict(row) for row in rows] if rows else []
        except Exception as e:
            logger.error(f"선박 타입별 필터링 실패: {e}")
            return []

# 전역 서비스 인스턴스
db_service = DatabaseService()
ui_service = UIDataService(db_service)
ais_service = AISService(db_service)

