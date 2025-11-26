#!/usr/bin/env python3
"""
Match API (vssl_Tos_VsslNo, vssl_Port_VsslNo) 데이터 확인 스크립트
"""

import pymysql
from datetime import datetime
import json

def connect_to_database():
    """데이터베이스 연결"""
    try:
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("✅ MySQL 데이터베이스 연결 성공\n")
        return connection
    except Exception as e:
        print(f"❌ 데이터베이스 연결 오류: {e}")
        return None

def check_all_data_sources(connection):
    """모든 데이터 소스 통계"""
    try:
        cursor = connection.cursor()
        
        query = """
        SELECT 
            data_source,
            table_name,
            COUNT(*) as inspection_count,
            SUM(total_rows) as total_rows,
            MAX(created_at) as last_inspection,
            MAX(inspection_status) as last_status
        FROM data_inspection_info
        GROUP BY data_source, table_name
        ORDER BY last_inspection DESC
        """
        cursor.execute(query)
        
        results = cursor.fetchall()
        
        if results:
            print(f"\n{'='*80}")
            print(f"📈 데이터 소스별 통계")
            print(f"{'='*80}\n")
            
            for idx, row in enumerate(results, 1):
                print(f"[{idx}] {row['data_source']} / {row['table_name']}")
                print(f"    검사 횟수: {row['inspection_count']}")
                print(f"    총 레코드: {row['total_rows']}")
                print(f"    마지막 검사: {row['last_inspection']}")
                print(f"    마지막 상태: {row['last_status']}")
                print()
        else:
            print("⚠️  데이터 소스 통계가 없습니다.")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ 데이터 소스 통계 조회 오류: {e}")

def check_inspection_info(connection, table_name_pattern=None, limit=10):
    """검사 정보 조회"""
    try:
        cursor = connection.cursor()
        
        if table_name_pattern:
            query = """
            SELECT 
                inspection_id,
                table_name,
                data_source,
                total_rows,
                total_columns,
                inspection_type,
                inspection_status,
                start_time,
                end_time,
                processing_time_ms,
                created_at
            FROM data_inspection_info
            WHERE table_name LIKE %s OR data_source LIKE %s
            ORDER BY created_at DESC
            LIMIT %s
            """
            pattern = f"%{table_name_pattern}%"
            cursor.execute(query, (pattern, pattern, limit))
        else:
            query = """
            SELECT 
                inspection_id,
                table_name,
                data_source,
                total_rows,
                total_columns,
                inspection_type,
                inspection_status,
                start_time,
                end_time,
                processing_time_ms,
                created_at
            FROM data_inspection_info
            ORDER BY created_at DESC
            LIMIT %s
            """
            cursor.execute(query, (limit,))
        
        results = cursor.fetchall()
        
        if results:
            print(f"\n{'='*80}")
            print(f"📊 검사 정보 (최근 {len(results)}개)")
            print(f"{'='*80}\n")
            
            for idx, row in enumerate(results, 1):
                print(f"[{idx}] Inspection ID: {row['inspection_id']}")
                print(f"    데이터 소스: {row['data_source']}")
                print(f"    테이블명: {row['table_name']}")
                print(f"    검사 상태: {row['inspection_status']}")
                print(f"    총 행/열: {row['total_rows']} / {row['total_columns']}")
                print(f"    검사 타입: {row['inspection_type']}")
                print(f"    처리시간: {row['processing_time_ms']}ms")
                print(f"    생성일시: {row['created_at']}")
                print()
        else:
            print("⚠️  검사 정보가 없습니다.")
        
        cursor.close()
        return results
        
    except Exception as e:
        print(f"❌ 검사 정보 조회 오류: {e}")
        return []

def check_inspection_results(connection, inspection_id):
    """특정 검사의 결과 조회"""
    try:
        cursor = connection.cursor()
        
        query = """
        SELECT 
            check_type,
            check_name,
            message,
            status,
            severity,
            affected_rows,
            details,
            created_at
        FROM data_inspection_results
        WHERE inspection_id = %s
        ORDER BY check_type, check_name
        """
        cursor.execute(query, (inspection_id,))
        
        results = cursor.fetchall()
        
        if results:
            print(f"\n{'='*80}")
            print(f"🔍 검사 결과 - {inspection_id}")
            print(f"{'='*80}\n")
            
            for idx, row in enumerate(results, 1):
                print(f"[{idx}] {row['check_type']} - {row['check_name']}")
                print(f"    상태: {row['status']} ({row['severity']})")
                print(f"    영향받은 행: {row['affected_rows']}")
                print(f"    메시지: {row['message']}")
                if row['details']:
                    try:
                        details = json.loads(row['details']) if isinstance(row['details'], str) else row['details']
                        print(f"    상세정보:")
                        for key, value in details.items():
                            print(f"      - {key}: {value}")
                    except:
                        print(f"    상세정보: {row['details']}")
                print()
        else:
            print(f"⚠️  검사 ID {inspection_id}에 대한 결과가 없습니다.")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ 검사 결과 조회 오류: {e}")

def check_inspection_summary(connection, inspection_id):
    """검사 요약 조회"""
    try:
        cursor = connection.cursor()
        
        query = """
        SELECT 
            total_checks,
            passed_checks,
            failed_checks,
            warning_checks,
            error_checks,
            pass_rate,
            data_quality_score,
            summary_json,
            recommendations
        FROM data_inspection_summary
        WHERE inspection_id = %s
        """
        cursor.execute(query, (inspection_id,))
        
        result = cursor.fetchone()
        
        if result:
            print(f"\n{'='*80}")
            print(f"📈 검사 요약 - {inspection_id}")
            print(f"{'='*80}\n")
            
            print(f"총 검사: {result['total_checks']}")
            print(f"통과: {result['passed_checks']}")
            print(f"실패: {result['failed_checks']}")
            print(f"경고: {result['warning_checks']}")
            print(f"오류: {result['error_checks']}")
            print(f"통과율: {result['pass_rate']}%")
            print(f"데이터 품질 점수: {result['data_quality_score']}")
            
            if result['summary_json']:
                try:
                    summary = json.loads(result['summary_json']) if isinstance(result['summary_json'], str) else result['summary_json']
                    print(f"\n요약 정보:")
                    print(json.dumps(summary, ensure_ascii=False, indent=2))
                except:
                    pass
            
            if result['recommendations']:
                print(f"\n권장사항:")
                print(result['recommendations'])
            
            print()
        else:
            print(f"⚠️  검사 ID {inspection_id}에 대한 요약이 없습니다.")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ 검사 요약 조회 오류: {e}")

def check_response_data(connection, inspection_id):
    """API 응답 데이터 조회"""
    try:
        cursor = connection.cursor()
        
        query = """
        SELECT 
            data_source,
            data_type,
            raw_response_data,
            processed_data_count,
            data_columns,
            data_file_name,
            data_file_size_bytes,
            created_at
        FROM api_response_data
        WHERE inspection_id = %s
        """
        cursor.execute(query, (inspection_id,))
        
        result = cursor.fetchone()
        
        if result:
            print(f"\n{'='*80}")
            print(f"📦 API 응답 데이터 - {inspection_id}")
            print(f"{'='*80}\n")
            
            print(f"데이터 소스: {result['data_source']}")
            print(f"데이터 타입: {result['data_type']}")
            print(f"처리된 데이터 개수: {result['processed_data_count']}")
            
            if result['data_columns']:
                try:
                    columns = json.loads(result['data_columns']) if isinstance(result['data_columns'], str) else result['data_columns']
                    print(f"데이터 컬럼 ({len(columns)}개):")
                    for col in columns:
                        print(f"  - {col}")
                except:
                    print(f"데이터 컬럼: {result['data_columns']}")
            
            if result['data_file_name']:
                print(f"\n파일명: {result['data_file_name']}")
                print(f"파일 크기: {result['data_file_size_bytes']} bytes")
            
            print(f"생성일시: {result['created_at']}")
            
            # 원본 응답 데이터 표시
            if result['raw_response_data']:
                try:
                    raw_data = json.loads(result['raw_response_data']) if isinstance(result['raw_response_data'], str) else result['raw_response_data']
                    print(f"\n{'='*80}")
                    print(f"📄 원본 응답 데이터:")
                    print(f"{'='*80}")
                    print(json.dumps(raw_data, ensure_ascii=False, indent=2))
                except:
                    print(f"\n원본 응답 데이터 (RAW): {result['raw_response_data'][:500]}...")
            
            print()
        else:
            print(f"⚠️  검사 ID {inspection_id}에 대한 응답 데이터가 없습니다.")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ 응답 데이터 조회 오류: {e}")

def main():
    """메인 함수"""
    connection = connect_to_database()
    
    if not connection:
        return
    
    try:
        print("\n" + "="*80)
        print("🔍 Match API 데이터 확인")
        print("="*80)
        
        # 1. 모든 데이터 소스 통계
        check_all_data_sources(connection)
        
        # 2. vssl 관련 검사 정보
        print("\n" + "="*80)
        print("🔍 vssl 관련 검사 정보")
        print("="*80)
        results = check_inspection_info(connection, table_name_pattern="vssl", limit=20)
        
        # 3. 가장 최근 검사의 상세 정보
        if results:
            latest = results[0]
            inspection_id = latest['inspection_id']
            
            check_inspection_summary(connection, inspection_id)
            check_response_data(connection, inspection_id)
            check_inspection_results(connection, inspection_id)
        
    finally:
        if connection:
            connection.close()
            print("\n✅ 데이터베이스 연결 종료")

if __name__ == "__main__":
    main()
