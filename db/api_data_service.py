#!/usr/bin/env python3
"""
API 호출 정보와 응답 데이터를 관리하는 서비스
"""

import pymysql
import json
import pandas as pd
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from database_config import MYSQL_CONFIG

class APIDataService:
    """API 호출 정보 및 응답 데이터 관리 서비스"""
    
    def __init__(self, host=None, port=None, user=None, password=None, database=None, data_dir="data"):
        # database_config.py의 설정을 기본값으로 사용
        self.config = MYSQL_CONFIG.copy()
        if host:
            self.config['host'] = host
        if port:
            self.config['port'] = port
        if user:
            self.config['user'] = user
        if password:
            self.config['password'] = password
        if database:
            self.config['database'] = database
        
        # 데이터 저장 디렉토리
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
    
    def connect(self):
        """데이터베이스 연결"""
        try:
            connection = pymysql.connect(**self.config)
            return connection
        except Exception as e:
            print(f"데이터베이스 연결 실패: {e}")
            return None
    
    def save_api_call_info(self, call_info: Dict[str, Any]) -> bool:
        """API 호출 정보 저장"""
        try:
            connection = self.connect()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            sql = """
            INSERT INTO api_call_info (
                inspection_id, api_endpoint, request_params, request_headers,
                response_status_code, response_time_ms, data_retrieval_start_time,
                data_retrieval_end_time, data_retrieval_duration_ms,
                total_records_retrieved, data_file_path
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                call_info['inspection_id'],
                call_info['api_endpoint'],
                json.dumps(call_info['request_params'], ensure_ascii=False),
                json.dumps(call_info.get('request_headers', {}), ensure_ascii=False),
                call_info.get('response_status_code'),
                call_info.get('response_time_ms'),
                call_info.get('data_retrieval_start_time'),
                call_info.get('data_retrieval_end_time'),
                call_info.get('data_retrieval_duration_ms'),
                call_info.get('total_records_retrieved'),
                call_info.get('data_file_path')
            )
            
            cursor.execute(sql, values)
            connection.commit()
            connection.close()
            
            print(f"✅ API 호출 정보 저장 완료: {call_info['inspection_id']}")
            return True
            
        except Exception as e:
            print(f"❌ API 호출 정보 저장 실패: {e}")
            return False
    
    def save_response_data(self, response_data: Dict[str, Any]) -> bool:
        """API 응답 데이터 저장"""
        try:
            connection = self.connect()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            sql = """
            INSERT INTO api_response_data (
                inspection_id, data_source, data_type, raw_response_data,
                processed_data_count, data_columns, data_file_name,
                data_file_size_bytes, data_checksum
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                response_data['inspection_id'],
                response_data['data_source'],
                response_data['data_type'],
                json.dumps(response_data.get('raw_response_data', {}), ensure_ascii=False),
                response_data.get('processed_data_count', 0),
                json.dumps(response_data.get('data_columns', []), ensure_ascii=False),
                response_data.get('data_file_name'),
                response_data.get('data_file_size_bytes', 0),
                response_data.get('data_checksum')
            )
            
            cursor.execute(sql, values)
            connection.commit()
            connection.close()
            
            print(f"✅ API 응답 데이터 저장 완료: {response_data['inspection_id']}")
            return True
            
        except Exception as e:
            print(f"❌ API 응답 데이터 저장 실패: {e}")
            return False
    
    def save_data_to_csv(self, data: List[Dict], inspection_id: str, data_source: str, data_type: str) -> Dict[str, Any]:
        """데이터를 CSV 파일로 저장"""
        try:
            # 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{inspection_id}_{data_source}_{data_type}_{timestamp}.csv"
            filepath = os.path.join(self.data_dir, filename)
            
            # DataFrame으로 변환하여 CSV 저장
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            # 파일 정보 계산
            file_size = os.path.getsize(filepath)
            checksum = self.calculate_file_checksum(filepath)
            
            result = {
                'data_file_name': filename,
                'data_file_path': filepath,
                'data_file_size_bytes': file_size,
                'data_checksum': checksum,
                'processed_data_count': len(data),
                'data_columns': list(df.columns)
            }
            
            print(f"✅ CSV 파일 저장 완료: {filename} ({len(data)}개 레코드)")
            return result
            
        except Exception as e:
            print(f"❌ CSV 파일 저장 실패: {e}")
            return {}
    
    def calculate_file_checksum(self, filepath: str) -> str:
        """파일 MD5 체크섬 계산"""
        try:
            hash_md5 = hashlib.md5()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"체크섬 계산 실패: {e}")
            return ""
    
    def get_api_call_info(self, inspection_id: str) -> Optional[Dict[str, Any]]:
        """API 호출 정보 조회"""
        try:
            connection = self.connect()
            if not connection:
                return None
            
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            sql = "SELECT * FROM api_call_info WHERE inspection_id = %s"
            cursor.execute(sql, (inspection_id,))
            
            result = cursor.fetchone()
            connection.close()
            
            return result
            
        except Exception as e:
            print(f"❌ API 호출 정보 조회 실패: {e}")
            return None
    
    def get_response_data(self, inspection_id: str) -> List[Dict[str, Any]]:
        """API 응답 데이터 조회"""
        try:
            connection = self.connect()
            if not connection:
                return []
            
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            sql = "SELECT * FROM api_response_data WHERE inspection_id = %s ORDER BY created_at"
            cursor.execute(sql, (inspection_id,))
            
            results = cursor.fetchall()
            connection.close()
            
            return results
            
        except Exception as e:
            print(f"❌ API 응답 데이터 조회 실패: {e}")
            return []
    
    def get_recent_api_calls(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 API 호출 목록 조회"""
        try:
            connection = self.connect()
            if not connection:
                return []
            
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            sql = """
            SELECT * FROM api_call_info 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            cursor.execute(sql, (limit,))
            
            results = cursor.fetchall()
            connection.close()
            
            return results
            
        except Exception as e:
            print(f"❌ 최근 API 호출 목록 조회 실패: {e}")
            return []
    
    def get_api_calls_by_endpoint(self, endpoint: str) -> List[Dict[str, Any]]:
        """엔드포인트별 API 호출 목록 조회"""
        try:
            connection = self.connect()
            if not connection:
                return []
            
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            sql = """
            SELECT * FROM api_call_info 
            WHERE api_endpoint = %s 
            ORDER BY created_at DESC
            """
            cursor.execute(sql, (endpoint,))
            
            results = cursor.fetchall()
            connection.close()
            
            return results
            
        except Exception as e:
            print(f"❌ 엔드포인트별 API 호출 목록 조회 실패: {e}")
            return []
    
    def load_csv_data(self, filepath: str) -> List[Dict[str, Any]]:
        """CSV 파일에서 데이터 로드"""
        try:
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            return df.to_dict('records')
        except Exception as e:
            print(f"❌ CSV 파일 로드 실패: {e}")
            return []
    
    def get_data_statistics(self, inspection_id: str) -> Dict[str, Any]:
        """데이터 통계 정보 조회"""
        try:
            connection = self.connect()
            if not connection:
                return {}
            
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            # API 호출 정보
            sql1 = "SELECT * FROM api_call_info WHERE inspection_id = %s"
            cursor.execute(sql1, (inspection_id,))
            call_info = cursor.fetchone()
            
            # 응답 데이터 정보
            sql2 = "SELECT * FROM api_response_data WHERE inspection_id = %s"
            cursor.execute(sql2, (inspection_id,))
            response_data = cursor.fetchall()
            
            connection.close()
            
            stats = {
                'inspection_id': inspection_id,
                'api_call_info': call_info,
                'response_data_count': len(response_data),
                'response_data': response_data,
                'total_files_size': sum(r.get('data_file_size_bytes', 0) for r in response_data),
                'total_records': sum(r.get('processed_data_count', 0) for r in response_data)
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ 데이터 통계 조회 실패: {e}")
            return {}

# 사용 예시
if __name__ == "__main__":
    service = APIDataService()
    
    # API 호출 정보 저장 예시
    call_info = {
        'inspection_id': 'test_123',
        'api_endpoint': '/TCWorkInfo/retrieveByTmnlIdTCWorkInfoList',
        'request_params': {
            'regNo': 'KETI',
            'tmnlId': 'BPTS',
            'timeFrom': '20211225000000',
            'timeTo': '20220108235959'
        },
        'request_headers': {
            'x-ncp-apigw-api-key': 'w4v69kgnlu',
            'accept': '*/*'
        },
        'response_status_code': 200,
        'response_time_ms': 1500,
        'data_retrieval_start_time': datetime.now(),
        'data_retrieval_end_time': datetime.now(),
        'data_retrieval_duration_ms': 5000,
        'total_records_retrieved': 67438,
        'data_file_path': '/path/to/tc_data.csv'
    }
    
    service.save_api_call_info(call_info)
    
    # 최근 API 호출 목록 조회
    recent_calls = service.get_recent_api_calls(5)
    print(f"최근 API 호출: {len(recent_calls)}개") 