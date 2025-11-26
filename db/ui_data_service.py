#!/usr/bin/env python3
"""
UI 데이터 서비스 클래스
UI에서 수집한 사용자 상호작용 데이터를 저장하고 조회하는 기능을 제공합니다.
"""

import pymysql
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from ui_database_config import UI_MYSQL_CONFIG

class UIDataService:
    """
    UI 데이터를 저장하고 조회하는 서비스 클래스
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or UI_MYSQL_CONFIG
        self.connection = None
    
    def connect(self):
        """데이터베이스 연결"""
        try:
            self.connection = pymysql.connect(**self.config)
            print(f"UI 데이터베이스 '{self.config['database']}'에 연결되었습니다.")
            return True
        except Exception as e:
            print(f"UI 데이터베이스 연결 실패: {e}")
            return False
    
    def disconnect(self):
        """데이터베이스 연결 해제"""
        if self.connection:
            self.connection.close()
            print("UI 데이터베이스 연결이 종료되었습니다.")
    
    def log_page_visit(self, user_id: str, page_name: str, page_url: str, 
                      login_status: str = 'visit', visit_duration: int = None,
                      session_id: str = None, ip_address: str = None, 
                      user_agent: str = None, referrer: str = None):
        """
        페이지 방문(로그인) 로그 저장
        
        Args:
            user_id: 사용자 ID
            page_name: 페이지 이름
            page_url: 페이지 URL
            login_status: 로그인 상태 ('login', 'logout', 'visit')
            visit_duration: 방문 시간 (초, 로그아웃 시에만)
            session_id: 세션 ID
            ip_address: IP 주소
            user_agent: 사용자 에이전트
            referrer: 참조 페이지
        """
        try:
            cursor = self.connection.cursor()
            
            insert_sql = """
            INSERT INTO page_visits 
            (user_id, page_name, page_url, login_status, visit_duration, session_id, ip_address, user_agent, referrer)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_sql, (
                user_id, page_name, page_url, login_status, visit_duration, session_id, 
                ip_address, user_agent, referrer
            ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"페이지 방문 로그 저장 실패: {e}")
            return False
    
    def log_api_call(self, user_id: str, api_endpoint: str, http_method: str,
                    request_data: Dict = None, response_status: int = None,
                    response_time_ms: int = None, session_id: str = None,
                    ip_address: str = None, user_agent: str = None, error_message: str = None):
        """
        API 호출 로그 저장
        
        Args:
            user_id: 사용자 ID
            api_endpoint: API 엔드포인트
            http_method: HTTP 메서드
            request_data: 요청 데이터 (JSON)
            response_status: 응답 상태 코드
            response_time_ms: 응답 시간 (밀리초)
            session_id: 세션 ID
            ip_address: IP 주소
            user_agent: 사용자 에이전트
            error_message: 에러 메시지
        """
        try:
            cursor = self.connection.cursor()
            
            insert_sql = """
            INSERT INTO api_calls 
            (user_id, api_endpoint, http_method, request_data, response_status, response_time_ms, 
             session_id, ip_address, user_agent, error_message)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_sql, (
                user_id, api_endpoint, http_method, json.dumps(request_data) if request_data else None,
                response_status, response_time_ms, session_id, ip_address, user_agent, error_message
            ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"API 호출 로그 저장 실패: {e}")
            return False
    
    def get_page_visits(self, user_id: str = None, login_status: str = None, limit: int = 100) -> List[Dict]:
        """
        페이지 방문 로그 조회
        
        Args:
            user_id: 특정 사용자 ID (선택사항)
            login_status: 로그인 상태 필터 (선택사항)
            limit: 조회할 레코드 수
        """
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            
            if user_id and login_status:
                query = "SELECT * FROM page_visits WHERE user_id = %s AND login_status = %s ORDER BY timestamp DESC LIMIT %s"
                cursor.execute(query, (user_id, login_status, limit))
            elif user_id:
                query = "SELECT * FROM page_visits WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s"
                cursor.execute(query, (user_id, limit))
            elif login_status:
                query = "SELECT * FROM page_visits WHERE login_status = %s ORDER BY timestamp DESC LIMIT %s"
                cursor.execute(query, (login_status, limit))
            else:
                query = "SELECT * FROM page_visits ORDER BY timestamp DESC LIMIT %s"
                cursor.execute(query, (limit,))
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"페이지 방문 로그 조회 실패: {e}")
            return []
    
    def get_api_calls(self, user_id: str = None, api_endpoint: str = None, limit: int = 100) -> List[Dict]:
        """
        API 호출 로그 조회
        
        Args:
            user_id: 특정 사용자 ID (선택사항)
            api_endpoint: 특정 API 엔드포인트 (선택사항)
            limit: 조회할 레코드 수
        """
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            
            if user_id and api_endpoint:
                query = "SELECT * FROM api_calls WHERE user_id = %s AND api_endpoint = %s ORDER BY timestamp DESC LIMIT %s"
                cursor.execute(query, (user_id, api_endpoint, limit))
            elif user_id:
                query = "SELECT * FROM api_calls WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s"
                cursor.execute(query, (user_id, limit))
            elif api_endpoint:
                query = "SELECT * FROM api_calls WHERE api_endpoint = %s ORDER BY timestamp DESC LIMIT %s"
                cursor.execute(query, (api_endpoint, limit))
            else:
                query = "SELECT * FROM api_calls ORDER BY timestamp DESC LIMIT %s"
                cursor.execute(query, (limit,))
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"API 호출 로그 조회 실패: {e}")
            return []
    
    def get_ui_statistics(self) -> Dict:
        """UI 데이터 통계 조회"""
        try:
            cursor = self.connection.cursor()
            
            stats = {}
            
            # 총 페이지 방문 수
            cursor.execute("SELECT COUNT(*) FROM page_visits")
            stats['total_page_visits'] = cursor.fetchone()[0]
            
            # 총 API 호출 수
            cursor.execute("SELECT COUNT(*) FROM api_calls")
            stats['total_api_calls'] = cursor.fetchone()[0]
            
            # 고유 사용자 수
            cursor.execute("SELECT COUNT(DISTINCT user_id) FROM page_visits")
            stats['unique_users'] = cursor.fetchone()[0]
            
            # 로그인 상태별 통계
            cursor.execute("""
                SELECT login_status, COUNT(*) as count 
                FROM page_visits 
                GROUP BY login_status
            """)
            stats['login_status_stats'] = cursor.fetchall()
            
            # 가장 많이 방문한 페이지
            cursor.execute("""
                SELECT page_name, COUNT(*) as visit_count 
                FROM page_visits 
                GROUP BY page_name 
                ORDER BY visit_count DESC 
                LIMIT 5
            """)
            stats['most_visited_pages'] = cursor.fetchall()
            
            # 가장 많이 호출된 API
            cursor.execute("""
                SELECT api_endpoint, COUNT(*) as call_count 
                FROM api_calls 
                GROUP BY api_endpoint 
                ORDER BY call_count DESC 
                LIMIT 5
            """)
            stats['most_called_apis'] = cursor.fetchall()
            
            # 평균 응답 시간
            cursor.execute("SELECT AVG(response_time_ms) FROM api_calls WHERE response_time_ms IS NOT NULL")
            avg_response_time = cursor.fetchone()[0]
            stats['avg_response_time_ms'] = round(avg_response_time, 2) if avg_response_time else 0
            
            return stats
            
        except Exception as e:
            print(f"UI 통계 조회 실패: {e}")
            return {}
    
    def get_user_activity_summary(self, user_id: str) -> Dict:
        """특정 사용자의 활동 요약"""
        try:
            cursor = self.connection.cursor()
            
            summary = {}
            
            # 사용자의 총 페이지 방문 수
            cursor.execute("SELECT COUNT(*) FROM page_visits WHERE user_id = %s", (user_id,))
            summary['total_page_visits'] = cursor.fetchone()[0]
            
            # 사용자의 총 API 호출 수
            cursor.execute("SELECT COUNT(*) FROM api_calls WHERE user_id = %s", (user_id,))
            summary['total_api_calls'] = cursor.fetchone()[0]
            
            # 사용자의 마지막 로그인 시간
            cursor.execute("""
                SELECT timestamp FROM page_visits 
                WHERE user_id = %s AND login_status = 'login' 
                ORDER BY timestamp DESC LIMIT 1
            """, (user_id,))
            last_login = cursor.fetchone()
            summary['last_login'] = last_login[0] if last_login else None
            
            # 사용자의 총 체류 시간 (로그아웃 시 기록된 시간의 합)
            cursor.execute("""
                SELECT SUM(visit_duration) FROM page_visits 
                WHERE user_id = %s AND login_status = 'logout' AND visit_duration IS NOT NULL
            """, (user_id,))
            total_duration = cursor.fetchone()[0]
            summary['total_duration_seconds'] = total_duration if total_duration else 0
            
            return summary
            
        except Exception as e:
            print(f"사용자 활동 요약 조회 실패: {e}")
            return {}
        
    def get_user_activity_summary(self, user_id: str) -> Dict:
        """특정 사용자의 활동 요약"""
        try:
            cursor = self.connection.cursor()
            
            summary = {}
            
            # 사용자의 총 페이지 방문 수
            cursor.execute("SELECT COUNT(*) FROM page_visits WHERE user_id = %s", (user_id,))
            summary['total_page_visits'] = cursor.fetchone()[0]
            
            # 사용자의 총 API 호출 수
            cursor.execute("SELECT COUNT(*) FROM api_calls WHERE user_id = %s", (user_id,))
            summary['total_api_calls'] = cursor.fetchone()[0]
            
            # 사용자의 마지막 로그인 시간
            cursor.execute("""
                SELECT timestamp FROM page_visits 
                WHERE user_id = %s AND login_status = 'login' 
                ORDER BY timestamp DESC LIMIT 1
            """, (user_id,))
            last_login = cursor.fetchone()
            summary['last_login'] = last_login[0] if last_login else None
            
            # 사용자의 총 체류 시간 (로그아웃 시 기록된 시간의 합)
            cursor.execute("""
                SELECT SUM(visit_duration) FROM page_visits 
                WHERE user_id = %s AND login_status = 'logout' AND visit_duration IS NOT NULL
            """, (user_id,))
            total_duration = cursor.fetchone()[0]
            summary['total_duration_seconds'] = total_duration if total_duration else 0
            
            return summary
            
        except Exception as e:
            print(f"사용자 활동 요약 조회 실패: {e}")
            return {}

    def get_time_based_statistics(self, period: str = 'daily', days: int = 30) -> Dict:
        """
        시간별 통계 조회
        
        Args:
            period: 'daily', 'weekly', 'monthly'
            days: 조회할 일수 (기본값: 30일)
        """
        try:
            cursor = self.connection.cursor()
            
            stats = {}
            
            if period == 'daily':
                # 일별 페이지 방문 통계
                cursor.execute("""
                    SELECT DATE(timestamp) as date, COUNT(*) as count 
                    FROM page_visits 
                    WHERE timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    GROUP BY DATE(timestamp) 
                    ORDER BY date
                """, (days,))
                stats['page_visits'] = cursor.fetchall()
                
                # 일별 API 호출 통계
                cursor.execute("""
                    SELECT DATE(timestamp) as date, COUNT(*) as count 
                    FROM api_calls 
                    WHERE timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    GROUP BY DATE(timestamp) 
                    ORDER BY date
                """, (days,))
                stats['api_calls'] = cursor.fetchall()
                
            elif period == 'weekly':
                # 주별 페이지 방문 통계
                cursor.execute("""
                    SELECT YEARWEEK(timestamp, 1) as week, COUNT(*) as count 
                    FROM page_visits 
                    WHERE timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    GROUP BY YEARWEEK(timestamp, 1) 
                    ORDER BY week
                """, (days,))
                stats['page_visits'] = cursor.fetchall()
                
                # 주별 API 호출 통계
                cursor.execute("""
                    SELECT YEARWEEK(timestamp, 1) as week, COUNT(*) as count 
                    FROM api_calls 
                    WHERE timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    GROUP BY YEARWEEK(timestamp, 1) 
                    ORDER BY week
                """, (days,))
                stats['api_calls'] = cursor.fetchall()
                
            elif period == 'monthly':
                # 월별 페이지 방문 통계
                cursor.execute("""
                    SELECT DATE_FORMAT(timestamp, '%%Y-%%m') as month, COUNT(*) as count 
                    FROM page_visits 
                    WHERE timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    GROUP BY DATE_FORMAT(timestamp, '%%Y-%%m') 
                    ORDER BY month
                """, (days,))
                stats['page_visits'] = cursor.fetchall()
                
                # 월별 API 호출 통계
                cursor.execute("""
                    SELECT DATE_FORMAT(timestamp, '%%Y-%%m') as month, COUNT(*) as count 
                    FROM api_calls 
                    WHERE timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    GROUP BY DATE_FORMAT(timestamp, '%%Y-%%m') 
                    ORDER BY month
                """, (days,))
                stats['api_calls'] = cursor.fetchall()
            
            return stats
            
        except Exception as e:
            print(f"시간별 통계 조회 실패: {e}")
            return {} 