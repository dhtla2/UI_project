#!/usr/bin/env python3
"""
API 호출 로그 확인 스크립트
"""

import pymysql
from datetime import datetime, timedelta

def check_api_logs():
    """API 호출 로그 상세 확인"""
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
            # 1. 전체 API 호출 통계
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(DISTINCT api_endpoint) as unique_endpoints,
                    AVG(response_time_ms) as avg_response_time,
                    MIN(response_time_ms) as min_response_time,
                    MAX(response_time_ms) as max_response_time
                FROM api_call_info
            """)
            stats = cursor.fetchone()
            
            print("📊 전체 API 호출 통계")
            print("=" * 60)
            print(f"총 호출 수: {stats[0]}개")
            print(f"고유 엔드포인트: {stats[1]}개")
            print(f"평균 응답 시간: {stats[2]:.2f}ms" if stats[2] else "평균 응답 시간: N/A")
            print(f"최소 응답 시간: {stats[3]}ms" if stats[3] else "최소 응답 시간: N/A")
            print(f"최대 응답 시간: {stats[4]}ms" if stats[4] else "최대 응답 시간: N/A")
            print()
            
            # 2. 오늘 API 호출 통계
            cursor.execute("""
                SELECT COUNT(*) FROM api_call_info 
                WHERE DATE(created_at) = CURDATE()
            """)
            today_count = cursor.fetchone()[0]
            print(f"📅 오늘 API 호출 수: {today_count}개\n")
            
            # 3. 최근 7일간 일별 통계
            cursor.execute("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as calls,
                    AVG(response_time_ms) as avg_ms
                FROM api_call_info 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """)
            
            print("📈 최근 7일간 일별 API 호출 통계")
            print("-" * 60)
            results = cursor.fetchall()
            if results:
                for row in results:
                    print(f"  {row[0]} | 호출: {row[1]}회 | 평균 응답: {row[2]:.0f}ms" if row[2] else f"  {row[0]} | 호출: {row[1]}회")
            else:
                print("  (데이터 없음)")
            print()
            
            # 4. 엔드포인트별 호출 횟수 (상위 10개)
            cursor.execute("""
                SELECT 
                    api_endpoint,
                    COUNT(*) as count,
                    AVG(response_time_ms) as avg_ms,
                    MAX(created_at) as last_call
                FROM api_call_info
                GROUP BY api_endpoint
                ORDER BY count DESC
                LIMIT 10
            """)
            
            print("🔌 가장 많이 호출된 API (상위 10개)")
            print("-" * 60)
            results = cursor.fetchall()
            if results:
                for idx, row in enumerate(results, 1):
                    endpoint_name = row[0].split('/')[-1] if '/' in row[0] else row[0]
                    print(f"  {idx}. {endpoint_name}")
                    print(f"     호출: {row[1]}회 | 평균: {row[2]:.0f}ms | 마지막: {row[3]}" if row[2] else f"     호출: {row[1]}회 | 마지막: {row[3]}")
            else:
                print("  (데이터 없음)")
            print()
            
            # 5. 최근 10개 API 호출
            cursor.execute("""
                SELECT 
                    api_endpoint,
                    inspection_id,
                    response_time_ms,
                    created_at
                FROM api_call_info
                ORDER BY created_at DESC
                LIMIT 10
            """)
            
            print("🕒 최근 10개 API 호출")
            print("-" * 60)
            results = cursor.fetchall()
            if results:
                for idx, row in enumerate(results, 1):
                    endpoint_name = row[0].split('/')[-1] if '/' in row[0] else row[0]
                    print(f"  [{idx}] {row[3]}")
                    print(f"      API: {endpoint_name}")
                    print(f"      검사 ID: {row[1]}")
                    print(f"      응답 시간: {row[2]}ms" if row[2] else "      응답 시간: N/A")
                    print()
            else:
                print("  (데이터 없음)")
            
            # 6. 느린 API 찾기 (응답 시간 > 3000ms)
            cursor.execute("""
                SELECT 
                    api_endpoint,
                    response_time_ms,
                    created_at
                FROM api_call_info
                WHERE response_time_ms > 3000
                ORDER BY response_time_ms DESC
                LIMIT 5
            """)
            
            print("⚠️  느린 API 호출 (3초 이상, 상위 5개)")
            print("-" * 60)
            results = cursor.fetchall()
            if results:
                for idx, row in enumerate(results, 1):
                    endpoint_name = row[0].split('/')[-1] if '/' in row[0] else row[0]
                    print(f"  {idx}. {endpoint_name}")
                    print(f"     응답 시간: {row[1]}ms ({row[1]/1000:.2f}초)")
                    print(f"     호출 시각: {row[2]}")
            else:
                print("  (모든 API가 3초 이내 응답 ✅)")
            print()
            
            # 7. 검사 ID별 API 호출 확인 (최근 검사)
            cursor.execute("""
                SELECT 
                    inspection_id,
                    COUNT(*) as api_count,
                    SUM(response_time_ms) as total_time,
                    MAX(created_at) as last_time
                FROM api_call_info
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)
                GROUP BY inspection_id
                ORDER BY last_time DESC
                LIMIT 5
            """)
            
            print("🔍 최근 검사별 API 호출 내역 (최근 5개)")
            print("-" * 60)
            results = cursor.fetchall()
            if results:
                for idx, row in enumerate(results, 1):
                    print(f"  [{idx}] 검사 ID: {row[0]}")
                    print(f"      API 호출 수: {row[1]}개")
                    print(f"      총 소요 시간: {row[2]}ms ({row[2]/1000:.2f}초)" if row[2] else "      총 소요 시간: N/A")
                    print(f"      마지막 호출: {row[3]}")
                    print()
            else:
                print("  (최근 24시간 내 검사 없음)")
        
        connection.close()
        print("✅ 데이터베이스 연결 종료")
        
    except pymysql.err.OperationalError as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        print("\n💡 확인사항:")
        print("  1. MySQL 서버가 실행 중인가요?")
        print("  2. 포트 3307이 열려있나요?")
        print("  3. 데이터베이스 'port_database'가 존재하나요?")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    check_api_logs()

