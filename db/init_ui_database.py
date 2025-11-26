#!/usr/bin/env python3
"""
UI 데이터베이스 초기화 스크립트
UI에서 수집한 사용자 상호작용 데이터를 저장할 데이터베이스와 테이블을 생성합니다.
"""

import pymysql
import json
from ui_database_config import (
    UI_MYSQL_CONFIG, 
    CREATE_UI_DATABASE_SQL,
    CREATE_PAGE_VISITS_TABLE_SQL,
    CREATE_API_CALLS_TABLE_SQL
)
import sys
import os

def create_ui_database():
    """UI 데이터베이스 생성"""
    try:
        # 데이터베이스 없이 연결
        connection = pymysql.connect(
            host=UI_MYSQL_CONFIG['host'],
            port=UI_MYSQL_CONFIG['port'],
            user=UI_MYSQL_CONFIG['user'],
            password=UI_MYSQL_CONFIG['password'],
            charset=UI_MYSQL_CONFIG['charset']
        )
        
        cursor = connection.cursor()
        
        # 데이터베이스 생성
        cursor.execute(CREATE_UI_DATABASE_SQL)
        print("데이터베이스 'ui_database'가 생성되었습니다.")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"UI 데이터베이스 생성 실패: {e}")
        return False

def create_ui_tables():
    """UI 관련 테이블들 생성"""
    try:
        connection = pymysql.connect(**UI_MYSQL_CONFIG)
        cursor = connection.cursor()
        
        # 테이블들 생성
        tables = [
            ("page_visits", CREATE_PAGE_VISITS_TABLE_SQL),
            ("api_calls", CREATE_API_CALLS_TABLE_SQL)
        ]
        
        for table_name, create_sql in tables:
            cursor.execute(create_sql)
            print(f"테이블 '{table_name}'이 생성되었습니다.")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"UI 테이블 생성 실패: {e}")
        return False

def insert_sample_data():
    """샘플 데이터 삽입 (테스트용)"""
    try:
        connection = pymysql.connect(**UI_MYSQL_CONFIG)
        cursor = connection.cursor()
        
        # 샘플 페이지 방문(로그인) 데이터
        sample_page_visits = [
            ("user1", "Dashboard", "/dashboard", "login", None, "session1", "127.0.0.1", "Mozilla/5.0", "/"),
            ("user1", "Dashboard", "/dashboard", "visit", None, "session1", "127.0.0.1", "Mozilla/5.0", "/"),
            ("user1", "Dashboard", "/dashboard", "logout", 180, "session1", "127.0.0.1", "Mozilla/5.0", "/"),
            ("user2", "Dashboard", "/dashboard", "login", None, "session2", "127.0.0.1", "Mozilla/5.0", "/"),
            ("user2", "Dashboard", "/dashboard", "visit", None, "session2", "127.0.0.1", "Mozilla/5.0", "/"),
        ]
        
        visit_insert_sql = """
        INSERT INTO page_visits 
        (user_id, page_name, page_url, login_status, visit_duration, session_id, ip_address, user_agent, referrer)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.executemany(visit_insert_sql, sample_page_visits)
        
        # 샘플 API 호출 데이터
        sample_api_calls = [
            ("user1", "/ais/statistics", "GET", '{}', 200, 150, "session1", "127.0.0.1", "Mozilla/5.0", None),
            ("user1", "/ais/all", "GET", '{"limit": 100}', 200, 200, "session1", "127.0.0.1", "Mozilla/5.0", None),
            ("user2", "/ais/statistics", "GET", '{}', 200, 120, "session2", "127.0.0.1", "Mozilla/5.0", None),
        ]
        
        api_insert_sql = """
        INSERT INTO api_calls 
        (user_id, api_endpoint, http_method, request_data, response_status, response_time_ms, session_id, ip_address, user_agent, error_message)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.executemany(api_insert_sql, sample_api_calls)
        
        connection.commit()
        print("샘플 데이터가 성공적으로 삽입되었습니다.")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"샘플 데이터 삽입 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("UI 데이터베이스 초기화를 시작합니다...")
    
    # 1. UI 데이터베이스 생성
    if not create_ui_database():
        print("UI 데이터베이스 생성에 실패했습니다.")
        return
    
    # 2. UI 테이블들 생성
    if not create_ui_tables():
        print("UI 테이블 생성에 실패했습니다.")
        return
    
    # 3. 샘플 데이터 삽입 (선택사항)
    insert_sample = input("샘플 데이터를 삽입하시겠습니까? (y/n): ").strip().lower()
    if insert_sample == 'y':
        if insert_sample_data():
            print("샘플 데이터 삽입이 완료되었습니다.")
        else:
            print("샘플 데이터 삽입에 실패했습니다.")
    else:
        print("샘플 데이터 삽입을 건너뛰었습니다.")
    
    print("UI 데이터베이스 초기화가 완료되었습니다.")
    print("\n생성된 테이블들:")
    print("- page_visits: 사용자 페이지 방문(로그인) 로그")
    print("- api_calls: API 호출 로그 (추후 업데이트 예정)")

if __name__ == "__main__":
    main() 