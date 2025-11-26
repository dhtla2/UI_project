#!/usr/bin/env python3
"""
UI 데이터베이스 데이터 확인 스크립트
실제로 저장된 데이터를 확인하고 분석합니다.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'db'))

from ui_data_service import UIDataService
import json
from datetime import datetime

def check_ui_database():
    """UI 데이터베이스의 데이터를 확인하고 출력"""
    
    # UI 데이터 서비스 인스턴스 생성
    ui_service = UIDataService()
    
    # 데이터베이스 연결
    if not ui_service.connect():
        print("❌ UI 데이터베이스 연결에 실패했습니다.")
        return
    
    print("✅ UI 데이터베이스에 연결되었습니다.\n")
    
    try:
        # 1. 전체 통계 확인
        print("📊 === UI 데이터베이스 전체 통계 ===")
        stats = ui_service.get_ui_statistics()
        
        if not stats:
            print("❌ 통계 데이터를 가져올 수 없습니다.")
            return
        
        print(f"총 페이지 방문 수: {stats.get('total_page_visits', 0)}")
        print(f"총 API 호출 수: {stats.get('total_api_calls', 0)}")
        print(f"고유 사용자 수: {stats.get('unique_users', 0)}")
        print(f"평균 응답 시간: {stats.get('avg_response_time_ms', 0):.2f}ms")
        
        # 로그인 상태별 통계
        print("\n🔐 로그인 상태별 통계:")
        login_stats = stats.get('login_status_stats', [])
        for status, count in login_stats:
            print(f"  - {status}: {count}회")
        
        # 가장 많이 방문한 페이지
        print("\n📄 가장 많이 방문한 페이지:")
        most_visited = stats.get('most_visited_pages', [])
        for page, count in most_visited:
            print(f"  - {page}: {count}회")
        
        # 가장 많이 호출된 API
        print("\n🌐 가장 많이 호출된 API:")
        most_called = stats.get('most_called_apis', [])
        for endpoint, count in most_called:
            print(f"  - {endpoint}: {count}회")
        
        # 2. 최근 페이지 방문 로그 확인
        print("\n📝 === 최근 페이지 방문 로그 (최대 10개) ===")
        page_visits = ui_service.get_page_visits(limit=10)
        
        if page_visits:
            for visit in page_visits:
                print(f"사용자: {visit['user_id']}")
                print(f"페이지: {visit['page_name']} ({visit['page_url']})")
                print(f"상태: {visit['login_status']}")
                print(f"시간: {visit['timestamp']}")
                if visit['visit_duration']:
                    print(f"방문 시간: {visit['visit_duration']}초")
                print(f"IP: {visit['ip_address']}")
                print("-" * 50)
        else:
            print("페이지 방문 로그가 없습니다.")
        
        # 3. 최근 API 호출 로그 확인
        print("\n🔌 === 최근 API 호출 로그 (최대 10개) ===")
        api_calls = ui_service.get_api_calls(limit=10)
        
        if api_calls:
            for call in api_calls:
                print(f"사용자: {call['user_id']}")
                print(f"API: {call['http_method']} {call['api_endpoint']}")
                print(f"상태: {call['response_status']}")
                print(f"응답 시간: {call['response_time_ms']}ms")
                print(f"시간: {call['timestamp']}")
                if call['error_message']:
                    print(f"에러: {call['error_message']}")
                print("-" * 50)
        else:
            print("API 호출 로그가 없습니다.")
        
        # 4. 테이블 구조 확인
        print("\n🗄️ === 테이블 구조 확인 ===")
        cursor = ui_service.connection.cursor()
        
        # page_visits 테이블 구조
        cursor.execute("DESCRIBE page_visits")
        print("📋 page_visits 테이블 구조:")
        for field in cursor.fetchall():
            print(f"  - {field[0]}: {field[1]} ({field[2]})")
        
        # api_calls 테이블 구조
        cursor.execute("DESCRIBE api_calls")
        print("\n📋 api_calls 테이블 구조:")
        for field in cursor.fetchall():
            print(f"  - {field[0]}: {field[1]} ({field[2]})")
        
        # 5. 샘플 데이터 추가 (테스트용)
        print("\n🧪 === 테스트 데이터 추가 ===")
        
        # 페이지 방문 로그 추가
        test_visits = [
            ("user1", "Dashboard", "/dashboard", "visit"),
            ("user2", "AIS Data", "/ais-data", "login"),
            ("user1", "Statistics", "/statistics", "visit"),
            ("user3", "Dashboard", "/dashboard", "logout"),
            ("user2", "Settings", "/settings", "visit")
        ]
        
        for user_id, page_name, page_url, login_status in test_visits:
            success = ui_service.log_page_visit(
                user_id=user_id,
                page_name=page_name,
                page_url=page_url,
                login_status=login_status,
                ip_address="127.0.0.1",
                user_agent="Test Browser"
            )
            if success:
                print(f"✅ 페이지 방문 로그 추가: {user_id} - {page_name}")
            else:
                print(f"❌ 페이지 방문 로그 추가 실패: {user_id} - {page_name}")
        
        # API 호출 로그 추가
        test_apis = [
            ("user1", "/ais/all", "GET", 200, 150),
            ("user2", "/ais/statistics", "GET", 200, 200),
            ("user1", "/ui/statistics", "GET", 200, 100),
            ("user3", "/ais/mmsi/123456789", "GET", 404, 50),
            ("user2", "/ais/flag/Korea", "GET", 200, 180)
        ]
        
        for user_id, endpoint, method, status, response_time in test_apis:
            success = ui_service.log_api_call(
                user_id=user_id,
                api_endpoint=endpoint,
                http_method=method,
                response_status=status,
                response_time_ms=response_time,
                ip_address="127.0.0.1",
                user_agent="Test Browser"
            )
            if success:
                print(f"✅ API 호출 로그 추가: {user_id} - {method} {endpoint}")
            else:
                print(f"❌ API 호출 로그 추가 실패: {user_id} - {method} {endpoint}")
        
        print("\n🔄 === 업데이트된 통계 ===")
        updated_stats = ui_service.get_ui_statistics()
        print(f"총 페이지 방문 수: {updated_stats.get('total_page_visits', 0)}")
        print(f"총 API 호출 수: {updated_stats.get('total_api_calls', 0)}")
        print(f"고유 사용자 수: {updated_stats.get('unique_users', 0)}")
        
    except Exception as e:
        print(f"❌ 데이터 확인 중 오류 발생: {e}")
    
    finally:
        # 데이터베이스 연결 해제
        ui_service.disconnect()
        print("\n🔌 데이터베이스 연결이 종료되었습니다.")

if __name__ == "__main__":
    check_ui_database() 