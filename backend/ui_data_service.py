import pymysql
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json

class UIDataService:
    def __init__(self):
        self.connection = None
        self.host = 'localhost'
        self.port = 3307
        self.user = 'root'
        self.password = 'Keti1234!'
        self.database = 'port_database'
        
    def connect(self):
        """데이터베이스 연결"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4'
            )
            return True
        except Exception as e:
            print(f"데이터베이스 연결 실패: {e}")
            return False
    
    def log_page_visit(self, user_id: str, page_name: str, page_url: str, 
                      login_status: str, visit_duration: Optional[int] = None,
                      session_id: Optional[str] = None, ip_address: Optional[str] = None,
                      user_agent: Optional[str] = None, referrer: Optional[str] = None,
                      visit_hour: Optional[int] = None, visit_weekday: Optional[int] = None):
        """페이지 방문 로그 저장"""
        print(f"[DEBUG] log_page_visit 호출됨 - user_id: {user_id}, page_name: {page_name}")
        try:
            # 매번 새로운 연결 생성
            print("[DEBUG] 새로운 DB 연결 생성")
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4'
            )
            
            print("[DEBUG] DB 커서 생성")
            with connection.cursor() as cursor:
                print("[DEBUG] INSERT 쿼리 실행")
                cursor.execute("""
                    INSERT INTO ui_log_page_visits 
                    (user_id, page_name, page_url, login_status, visit_duration, 
                     session_id, ip_address, user_agent, referrer, created_at, visit_hour, visit_weekday)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, page_name, page_url, login_status, visit_duration,
                      session_id, ip_address, user_agent, referrer, datetime.now(),
                      visit_hour, visit_weekday))
                
                print("[DEBUG] 커밋 실행")
                connection.commit()
                print("[DEBUG] 로그 저장 성공")
                return True
                
        except Exception as e:
            print(f"[DEBUG] 페이지 방문 로그 저장 실패: {e}")
            return False
        finally:
            if 'connection' in locals():
                connection.close()
    
    def get_ui_statistics(self):
        """UI 통계 데이터 조회"""
        try:
            if not self.connection:
                self.connect()
            
            with self.connection.cursor() as cursor:
                # 총 페이지 방문 수
                cursor.execute("SELECT COUNT(*) FROM ui_log_page_visits")
                total_visits = cursor.fetchone()[0]
                
                # 고유 사용자 수
                cursor.execute("SELECT COUNT(DISTINCT user_id) FROM ui_log_page_visits")
                unique_users = cursor.fetchone()[0]
                
                # 오늘 방문 수
                cursor.execute("""
                    SELECT COUNT(*) FROM ui_log_page_visits 
                    WHERE DATE(created_at) = CURDATE()
                """)
                today_visits = cursor.fetchone()[0]
                
                return {
                    "total_visits": total_visits,
                    "unique_users": unique_users,
                    "today_visits": today_visits
                }
                
        except Exception as e:
            print(f"UI 통계 조회 실패: {e}")
            return {
                "total_visits": 0,
                "unique_users": 0,
                "today_visits": 0
            }
    
    def get_user_activity_summary(self, user_id: str):
        """특정 사용자의 활동 요약"""
        try:
            if not self.connection:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT page_name, COUNT(*) as visit_count, 
                           MAX(created_at) as last_visit
                    FROM ui_log_page_visits 
                    WHERE user_id = %s
                    GROUP BY page_name
                    ORDER BY visit_count DESC
                """, (user_id,))
                
                activities = []
                for row in cursor.fetchall():
                    activities.append({
                        "page_name": row[0],
                        "visit_count": row[1],
                        "last_visit": row[2].isoformat() if row[2] else None
                    })
                
                return {"user_id": user_id, "activities": activities}
                
        except Exception as e:
            print(f"사용자 활동 조회 실패: {e}")
            return {"user_id": user_id, "activities": []}
    
    def get_page_visits(self, user_id: Optional[str] = None, 
                       login_status: Optional[str] = None, limit: int = 100):
        """페이지 방문 로그 조회"""
        try:
            if not self.connection:
                self.connect()
            
            query = "SELECT * FROM ui_log_page_visits WHERE 1=1"
            params = []
            
            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)
            
            if login_status:
                query += " AND login_status = %s"
                params.append(login_status)
            
            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)
            
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                
                visits = []
                for row in cursor.fetchall():
                    visits.append({
                        "id": row[0],
                        "user_id": row[1],
                        "page_name": row[2],
                        "page_url": row[3],
                        "login_status": row[4],
                        "visit_duration": row[5],
                        "session_id": row[6],
                        "ip_address": row[7],
                        "user_agent": row[8],
                        "referrer": row[9],
                        "created_at": row[10].isoformat() if row[10] else None
                    })
                
                return visits
                
        except Exception as e:
            print(f"페이지 방문 로그 조회 실패: {e}")
            return []
    
    def get_connection(self):
        """데이터베이스 연결 반환"""
        if not self.connection:
            self.connect()
        return self.connection
    
    def log_api_call(self, endpoint: str, method: str, status_code: int, 
                     response_time: Optional[float] = None, user_id: Optional[str] = None,
                     ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """API 호출 로그 저장"""
        try:
            if not self.connection:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO api_call_logs 
                    (endpoint, method, status_code, response_time, user_id, 
                     ip_address, user_agent, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (endpoint, method, status_code, response_time, user_id,
                      ip_address, user_agent, datetime.now()))
                
                self.connection.commit()
                return True
                
        except Exception as e:
            print(f"API 호출 로그 저장 실패: {e}")
            return False