#!/usr/bin/env python3
"""
페이지 방문 로그 확인 스크립트
"""

import pymysql
from datetime import datetime, timedelta

def check_page_visits():
    """페이지 방문 로그 확인"""
    try:
        # 데이터베이스 연결
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        
        print("✅ 데이터베이스 연결 성공\n")
        
        with connection.cursor() as cursor:
            # 1. 전체 페이지 방문 수
            cursor.execute("SELECT COUNT(*) FROM ui_log_page_visits")
            total_count = cursor.fetchone()[0]
            print(f"📊 총 페이지 방문 수: {total_count}개\n")
            
            # 2. 고유 사용자 수
            cursor.execute("SELECT COUNT(DISTINCT user_id) FROM ui_log_page_visits")
            unique_users = cursor.fetchone()[0]
            print(f"👥 고유 사용자 수: {unique_users}명\n")
            
            # 3. 오늘 방문 수
            cursor.execute("""
                SELECT COUNT(*) FROM ui_log_page_visits 
                WHERE DATE(created_at) = CURDATE()
            """)
            today_count = cursor.fetchone()[0]
            print(f"📅 오늘 방문 수: {today_count}개\n")
            
            # 4. 최근 7일간 일별 통계
            cursor.execute("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as visits,
                    COUNT(DISTINCT user_id) as unique_users
                FROM ui_log_page_visits 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """)
            
            print("📈 최근 7일간 일별 통계:")
            print("-" * 60)
            results = cursor.fetchall()
            if results:
                for row in results:
                    print(f"  날짜: {row[0]} | 방문: {row[1]}회 | 고유 사용자: {row[2]}명")
            else:
                print("  (데이터 없음)")
            print()
            
            # 5. 페이지별 방문 통계
            cursor.execute("""
                SELECT page_name, COUNT(*) as count
                FROM ui_log_page_visits
                GROUP BY page_name
                ORDER BY count DESC
                LIMIT 10
            """)
            
            print("📄 페이지별 방문 통계 (상위 10개):")
            print("-" * 60)
            results = cursor.fetchall()
            if results:
                for idx, row in enumerate(results, 1):
                    print(f"  {idx}. {row[0]}: {row[1]}회")
            else:
                print("  (데이터 없음)")
            print()
            
            # 6. 최근 10개 방문 로그
            cursor.execute("""
                SELECT user_id, page_name, page_url, login_status, 
                       created_at, ip_address, visit_hour
                FROM ui_log_page_visits
                ORDER BY created_at DESC
                LIMIT 10
            """)
            
            print("🕒 최근 10개 방문 로그:")
            print("-" * 60)
            results = cursor.fetchall()
            if results:
                for idx, row in enumerate(results, 1):
                    print(f"  [{idx}] {row[4]} | 사용자: {row[0]}")
                    print(f"      페이지: {row[1]} ({row[2]})")
                    print(f"      상태: {row[3]} | IP: {row[5]} | 시간대: {row[6]}시")
                    print()
            else:
                print("  (데이터 없음)\n")
            
            # 7. 시간대별 방문 패턴
            cursor.execute("""
                SELECT visit_hour, COUNT(*) as count
                FROM ui_log_page_visits
                WHERE visit_hour IS NOT NULL
                GROUP BY visit_hour
                ORDER BY visit_hour
            """)
            
            print("⏰ 시간대별 방문 패턴:")
            print("-" * 60)
            results = cursor.fetchall()
            if results:
                for row in results:
                    bar = "█" * (row[1] // max(1, max([r[1] for r in results]) // 20))
                    print(f"  {row[0]:2d}시: {bar} ({row[1]}회)")
            else:
                print("  (데이터 없음)")
            print()
            
            # 8. API 호출 수 확인
            cursor.execute("SELECT COUNT(*) FROM api_call_info")
            api_count = cursor.fetchone()[0]
            print(f"🔌 총 API 호출 수: {api_count}개\n")
            
            # 9. 최근 API 호출
            if api_count > 0:
                cursor.execute("""
                    SELECT api_endpoint, response_status_code, 
                           response_time_ms, created_at
                    FROM api_call_info
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                
                print("🌐 최근 5개 API 호출:")
                print("-" * 60)
                results = cursor.fetchall()
                for idx, row in enumerate(results, 1):
                    print(f"  [{idx}] {row[3]}")
                    print(f"      엔드포인트: {row[0]}")
                    print(f"      상태: {row[1]} | 응답시간: {row[2]}ms")
                    print()
        
        connection.close()
        print("✅ 데이터베이스 연결 종료")
        
    except pymysql.err.OperationalError as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        print("\n💡 확인사항:")
        print("  1. MySQL 서버가 실행 중인가요?")
        print("  2. 포트 3307이 열려있나요?")
        print("  3. 데이터베이스 'port_database'가 존재하나요?")
        print("  4. 사용자 'root'의 비밀번호가 'Keti1234!'인가요?")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    check_page_visits()

