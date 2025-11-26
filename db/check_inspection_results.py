#!/usr/bin/env python3
"""
검사 결과 상세 확인 스크립트

이 스크립트는 특정 inspection_id에 대한 모든 검사 결과 데이터를
데이터베이스에서 조회하여 상세하게 출력합니다.

사용법:
    python check_inspection_results.py [inspection_id]
    
예시:
    python check_inspection_results.py tc_inspection_1755499923_e1c242
"""

import pymysql
import json
from datetime import datetime
from typing import Dict, Any, Optional
from database_config import MYSQL_CONFIG

class InspectionResultChecker:
    """검사 결과 확인 클래스"""
    
    def __init__(self):
        self.config = MYSQL_CONFIG.copy()
    
    def connect(self):
        """데이터베이스 연결"""
        try:
            connection = pymysql.connect(**self.config)
            return connection
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            return None
    
    def check_inspection_info(self, inspection_id: str) -> Optional[Dict[str, Any]]:
        """검사 기본 정보 확인"""
        try:
            connection = self.connect()
            if not connection:
                return None
            
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT * FROM data_inspection_info WHERE inspection_id = %s"
            cursor.execute(sql, (inspection_id,))
            result = cursor.fetchone()
            
            connection.close()
            return result
            
        except Exception as e:
            print(f"❌ 검사 정보 조회 실패: {e}")
            return None
    
    def check_inspection_results(self, inspection_id: str) -> list:
        """검사 결과 상세 확인"""
        try:
            connection = self.connect()
            if not connection:
                return []
            
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = """
            SELECT check_type, check_name, message, status, severity, 
                   affected_rows, affected_columns, details
            FROM data_inspection_results 
            WHERE inspection_id = %s
            ORDER BY check_type, check_name
            """
            cursor.execute(sql, (inspection_id,))
            results = cursor.fetchall()
            
            connection.close()
            return results
            
        except Exception as e:
            print(f"❌ 검사 결과 조회 실패: {e}")
            return []
    
    def check_inspection_summary(self, inspection_id: str) -> Optional[Dict[str, Any]]:
        """검사 요약 정보 확인"""
        try:
            connection = self.connect()
            if not connection:
                return None
            
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT * FROM data_inspection_summary WHERE inspection_id = %s"
            cursor.execute(sql, (inspection_id,))
            result = cursor.fetchone()
            
            connection.close()
            return result
            
        except Exception as e:
            print(f"❌ 검사 요약 조회 실패: {e}")
            return None
    
    def check_api_call_info(self, inspection_id: str) -> Optional[Dict[str, Any]]:
        """API 호출 정보 확인"""
        try:
            connection = self.connect()
            if not connection:
                return None
            
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = """
            SELECT api_endpoint, request_params, request_headers, response_status_code,
                   response_time_ms, data_retrieval_start_time, data_retrieval_end_time,
                   data_retrieval_duration_ms, total_records_retrieved, data_file_path
            FROM api_call_info 
            WHERE inspection_id = %s
            """
            cursor.execute(sql, (inspection_id,))
            result = cursor.fetchone()
            
            connection.close()
            return result
            
        except Exception as e:
            print(f"❌ API 호출 정보 조회 실패: {e}")
            return None
    
    def check_api_response_data(self, inspection_id: str) -> Optional[Dict[str, Any]]:
        """API 응답 데이터 확인"""
        try:
            connection = self.connect()
            if not connection:
                return None
            
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = """
            SELECT data_source, data_type, raw_response_data, processed_data_count,
                   data_columns, data_file_name, data_file_size_bytes, data_checksum
            FROM api_response_data 
            WHERE inspection_id = %s
            """
            cursor.execute(sql, (inspection_id,))
            result = cursor.fetchone()
            
            connection.close()
            return result
            
        except Exception as e:
            print(f"❌ API 응답 데이터 조회 실패: {e}")
            return None
    
    def check_work_info_tables(self, inspection_id: str) -> Dict[str, Any]:
        """작업 정보 테이블들 확인 (전체 데이터 현황)"""
        try:
            connection = self.connect()
            if not connection:
                return {}
            
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            tables = ['tc_work_info', 'qc_work_info', 'yt_work_info']
            results = {}
            
            for table in tables:
                # 전체 데이터 수 확인
                sql = f"SELECT COUNT(*) as count FROM {table}"
                cursor.execute(sql)
                count_result = cursor.fetchone()
                results[table] = count_result['count'] if count_result else 0
                
                # 최근 데이터 샘플 조회 (inspection_id와 무관)
                if results[table] > 0:
                    sql = f"SELECT * FROM {table} ORDER BY created_at DESC LIMIT 3"
                    cursor.execute(sql)
                    sample_data = cursor.fetchall()
                    results[f"{table}_sample"] = sample_data
            
            connection.close()
            return results
            
        except Exception as e:
            print(f"❌ 작업 정보 테이블 조회 실패: {e}")
            return {}
    
    def print_separator(self, title: str):
        """구분선 출력"""
        print("\n" + "="*80)
        print(f"📋 {title}")
        print("="*80)
    
    def print_inspection_info(self, info: Dict[str, Any]):
        """검사 기본 정보 출력"""
        if not info:
            print("❌ 검사 정보를 찾을 수 없습니다.")
            return
        
        print(f"🔍 검사 ID: {info['inspection_id']}")
        print(f"📊 데이터 소스: {info['data_source']}")
        print(f"📋 테이블명: {info['table_name']}")
        print(f"📈 총 행수: {info['total_rows']:,}")
        print(f"📊 총 컬럼수: {info['total_columns']}")
        print(f"🔧 검사 타입: {info['inspection_type']}")
        print(f"📝 검사 상태: {info['inspection_status']}")
        print(f"⏰ 시작 시간: {info['start_time']}")
        print(f"⏰ 종료 시간: {info['end_time']}")
        print(f"⏱️ 처리 시간: {info['processing_time_ms']}ms")
        print(f"👤 생성자: {info['created_by']}")
    
    def print_inspection_results(self, results: list):
        """검사 결과 상세 출력"""
        if not results:
            print("❌ 검사 결과를 찾을 수 없습니다.")
            return
        
        print(f"📊 총 검사 항목: {len(results)}개")
        
        # 검사 타입별로 그룹화
        by_type = {}
        for result in results:
            check_type = result['check_type']
            if check_type not in by_type:
                by_type[check_type] = []
            by_type[check_type].append(result)
        
        for check_type, type_results in by_type.items():
            print(f"\n🔍 {check_type} 검사 결과:")
            print("-" * 60)
            
            for result in type_results:
                status_emoji = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⚠️"
                print(f"{status_emoji} {result['check_name']}: {result['message']}")
                print(f"   📊 상태: {result['status']}")
                print(f"   🎯 심각도: {result['severity']}")
                print(f"   📈 영향 행수: {result['affected_rows']}")
                if result['affected_columns']:
                    print(f"   📋 영향 컬럼: {result['affected_columns']}")
                print()
    
    def print_inspection_summary(self, summary: Dict[str, Any]):
        """검사 요약 정보 출력"""
        if not summary:
            print("❌ 검사 요약을 찾을 수 없습니다.")
            return
        
        print(f"📊 총 검사 수: {summary['total_checks']}")
        print(f"✅ 통과: {summary['passed_checks']}")
        print(f"❌ 실패: {summary['failed_checks']}")
        print(f"⚠️ 경고: {summary['warning_checks']}")
        print(f"🚨 오류: {summary['error_checks']}")
        print(f"📈 통과율: {summary['pass_rate']:.2f}%")
        print(f"🎯 품질 점수: {summary['data_quality_score']:.2f}")
        print(f"💡 권장사항: {summary['recommendations']}")
    
    def print_api_call_info(self, api_info: Dict[str, Any]):
        """API 호출 정보 출력"""
        if not api_info:
            print("❌ API 호출 정보를 찾을 수 없습니다.")
            return
        
        print(f"🌐 API 엔드포인트: {api_info['api_endpoint']}")
        print(f"📤 요청 파라미터: {api_info['request_params']}")
        print(f"📋 응답 상태 코드: {api_info['response_status_code']}")
        print(f"⏱️ 응답 시간: {api_info['response_time_ms']}ms")
        print(f"📊 총 레코드 수: {api_info['total_records_retrieved']}")
        print(f"⏰ 데이터 수집 시작: {api_info['data_retrieval_start_time']}")
        print(f"⏰ 데이터 수집 종료: {api_info['data_retrieval_end_time']}")
        print(f"⏱️ 데이터 수집 시간: {api_info['data_retrieval_duration_ms']}ms")
        if api_info['data_file_path']:
            print(f"📁 데이터 파일 경로: {api_info['data_file_path']}")
    
    def print_api_response_data(self, response_data: Dict[str, Any]):
        """API 응답 데이터 출력"""
        if not response_data:
            print("❌ API 응답 데이터를 찾을 수 없습니다.")
            return
        
        print(f"📊 데이터 소스: {response_data['data_source']}")
        print(f"🔧 데이터 타입: {response_data['data_type']}")
        print(f"📈 처리된 데이터 수: {response_data['processed_data_count']}")
        print(f"📋 데이터 컬럼: {response_data['data_columns']}")
        if response_data['data_file_name']:
            print(f"📁 파일명: {response_data['data_file_name']}")
            print(f"📏 파일 크기: {response_data['data_file_size_bytes']:,} bytes")
            print(f"🔒 체크섬: {response_data['data_checksum']}")
    
    def print_work_info_tables(self, work_info: Dict[str, Any]):
        """작업 정보 테이블 출력"""
        if not work_info:
            print("❌ 작업 정보를 찾을 수 없습니다.")
            return
        
        print("📊 작업 정보 테이블별 전체 데이터 현황:")
        print("💡 참고: 이 테이블들은 실제 터미널 작업 데이터를 저장하며, 검사 결과와는 별개입니다.")
        
        for table in ['tc_work_info', 'qc_work_info', 'yt_work_info']:
            count = work_info.get(table, 0)
            print(f"   📋 {table}: {count:,}건")
            
            # 샘플 데이터가 있으면 출력
            sample_key = f"{table}_sample"
            if sample_key in work_info and work_info[sample_key]:
                print(f"   📝 {table} 최근 데이터 샘플 (최근 3건):")
                for i, sample in enumerate(work_info[sample_key][:3], 1):
                    # 주요 필드만 출력
                    if 'tmnlId' in sample:
                        print(f"      {i}. 터미널: {sample.get('tmnlId', 'N/A')}, 컨테이너: {sample.get('cntrNo', 'N/A')}, 작업시간: {sample.get('wkTime', 'N/A')}")
                    else:
                        print(f"      {i}. {sample}")
                print()
    
    def check_all(self, inspection_id: str):
        """모든 검사 결과 확인"""
        print(f"🔍 검사 ID '{inspection_id}'에 대한 상세 결과를 확인합니다...")
        
        # 1. 검사 기본 정보
        self.print_separator("검사 기본 정보")
        info = self.check_inspection_info(inspection_id)
        self.print_inspection_info(info)
        
        # 2. 검사 결과 상세
        self.print_separator("검사 결과 상세")
        results = self.check_inspection_results(inspection_id)
        self.print_inspection_results(results)
        
        # 3. 검사 요약
        self.print_separator("검사 요약")
        summary = self.check_inspection_summary(inspection_id)
        self.print_inspection_summary(summary)
        
        # 4. API 호출 정보
        self.print_separator("API 호출 정보")
        api_info = self.check_api_call_info(inspection_id)
        self.print_api_call_info(api_info)
        
        # 5. API 응답 데이터
        self.print_separator("API 응답 데이터")
        response_data = self.check_api_response_data(inspection_id)
        self.print_api_response_data(response_data)
        
        # 6. 작업 정보 테이블
        self.print_separator("작업 정보 테이블")
        work_info = self.check_work_info_tables(inspection_id)
        self.print_work_info_tables(work_info)
        
        print("\n" + "="*80)
        print("🎯 검사 결과 확인 완료!")
        print("="*80)

def main():
    """메인 함수"""
    import sys
    
    # inspection_id 설정 (명령행 인수 또는 기본값)
    if len(sys.argv) > 1:
        inspection_id = sys.argv[1]
    else:
        # 기본값으로 최근 검사 ID 사용
        inspection_id = "tc_inspection_1755499923_e1c242"  # 여기에 원하는 ID 입력
    
    print(f"🔍 검사 결과 확인 도구")
    print(f"📊 검사 ID: {inspection_id}")
    
    checker = InspectionResultChecker()
    checker.check_all(inspection_id)

if __name__ == "__main__":
    main()
