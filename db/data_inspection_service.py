#!/usr/bin/env python3
"""
데이터 검사 결과를 데이터베이스에 저장하고 조회하는 서비스
"""

import pymysql
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from database_config import MYSQL_CONFIG

class DataInspectionService:
    """데이터 검사 결과 관리 서비스"""
    
    def __init__(self, host=None, port=None, user=None, password=None, database=None):
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
    
    def connect(self):
        """데이터베이스 연결"""
        try:
            connection = pymysql.connect(**self.config)
            return connection
        except Exception as e:
            print(f"데이터베이스 연결 실패: {e}")
            return None
    
    def save_inspection_info(self, inspection_data: Dict[str, Any]) -> bool:
        """검사 정보 저장"""
        try:
            connection = self.connect()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            sql = """
            INSERT INTO data_inspection_info (
                inspection_id, table_name, data_source, total_rows, total_columns,
                inspection_type, inspection_status, start_time, end_time,
                processing_time_ms, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                inspection_data['inspection_id'],
                inspection_data['table_name'],
                inspection_data['data_source'],
                inspection_data['total_rows'],
                inspection_data['total_columns'],
                inspection_data['inspection_type'],
                inspection_data['inspection_status'],
                inspection_data.get('start_time'),
                inspection_data.get('end_time'),
                inspection_data.get('processing_time_ms'),
                inspection_data.get('created_by', 'system')
            )
            
            cursor.execute(sql, values)
            connection.commit()
            connection.close()
            
            print(f"✅ 검사 정보 저장 완료: {inspection_data['inspection_id']}")
            return True
            
        except Exception as e:
            print(f"❌ 검사 정보 저장 실패: {e}")
            return False
    
    def save_inspection_results(self, inspection_id: str, results: List[Dict[str, Any]]) -> bool:
        """검사 결과 상세 저장"""
        try:
            connection = self.connect()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            sql = """
            INSERT INTO data_inspection_results (
                inspection_id, check_type, check_name, message, status, severity,
                affected_rows, affected_columns, details
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for result in results:
                values = (
                    inspection_id,
                    result['check_type'],
                    result['check_name'],
                    result['message'],
                    result['status'],
                    result.get('severity', 'MEDIUM'),
                    result.get('affected_rows', 0),
                    json.dumps(result.get('affected_columns', []), ensure_ascii=False),
                    json.dumps(result.get('details', {}), ensure_ascii=False)
                )
                
                cursor.execute(sql, values)
            
            connection.commit()
            connection.close()
            
            print(f"✅ 검사 결과 저장 완료: {len(results)}개")
            return True
            
        except Exception as e:
            print(f"❌ 검사 결과 저장 실패: {e}")
            return False
    
    def save_inspection_summary(self, inspection_id: str, summary_data: Dict[str, Any]) -> bool:
        """검사 요약 저장"""
        try:
            connection = self.connect()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            sql = """
            INSERT INTO data_inspection_summary (
                inspection_id, total_checks, passed_checks, failed_checks,
                warning_checks, error_checks, pass_rate, data_quality_score,
                summary_json, recommendations
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                inspection_id,
                summary_data['total_checks'],
                summary_data['passed_checks'],
                summary_data['failed_checks'],
                summary_data.get('warning_checks', 0),
                summary_data.get('error_checks', 0),
                summary_data.get('pass_rate', 0.0),
                summary_data.get('data_quality_score', 0.0),
                json.dumps(summary_data.get('summary_json', {}), ensure_ascii=False),
                summary_data.get('recommendations', '')
            )
            
            cursor.execute(sql, values)
            connection.commit()
            connection.close()
            
            print(f"✅ 검사 요약 저장 완료: {inspection_id}")
            return True
            
        except Exception as e:
            print(f"❌ 검사 요약 저장 실패: {e}")
            return False
    
    def save_data_samples(self, inspection_id: str, samples: List[Dict[str, Any]]) -> bool:
        """데이터 샘플 저장"""
        try:
            connection = self.connect()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            sql = """
            INSERT INTO data_samples (
                inspection_id, sample_type, sample_data, sample_size, description
            ) VALUES (%s, %s, %s, %s, %s)
            """
            
            for sample in samples:
                values = (
                    inspection_id,
                    sample['sample_type'],
                    json.dumps(sample['sample_data'], ensure_ascii=False),
                    sample['sample_size'],
                    sample.get('description', '')
                )
                
                cursor.execute(sql, values)
            
            connection.commit()
            connection.close()
            
            print(f"✅ 데이터 샘플 저장 완료: {len(samples)}개")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 샘플 저장 실패: {e}")
            return False
    
    def get_inspection_info(self, inspection_id: str) -> Optional[Dict[str, Any]]:
        """검사 정보 조회"""
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
    
    def get_inspection_results(self, inspection_id: str) -> List[Dict[str, Any]]:
        """검사 결과 조회"""
        try:
            connection = self.connect()
            if not connection:
                return []
            
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            sql = "SELECT * FROM data_inspection_results WHERE inspection_id = %s ORDER BY created_at"
            cursor.execute(sql, (inspection_id,))
            
            results = cursor.fetchall()
            connection.close()
            
            return results
            
        except Exception as e:
            print(f"❌ 검사 결과 조회 실패: {e}")
            return []
    
    def get_inspection_summary(self, inspection_id: str) -> Optional[Dict[str, Any]]:
        """검사 요약 조회"""
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
    
    def get_recent_inspections(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 검사 목록 조회"""
        try:
            connection = self.connect()
            if not connection:
                return []
            
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            sql = """
            SELECT * FROM data_inspection_info 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            cursor.execute(sql, (limit,))
            
            results = cursor.fetchall()
            connection.close()
            
            return results
            
        except Exception as e:
            print(f"❌ 최근 검사 목록 조회 실패: {e}")
            return []
    
    def get_inspections_by_status(self, status: str) -> List[Dict[str, Any]]:
        """상태별 검사 목록 조회"""
        try:
            connection = self.connect()
            if not connection:
                return []
            
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            sql = """
            SELECT * FROM data_inspection_info 
            WHERE inspection_status = %s 
            ORDER BY created_at DESC
            """
            cursor.execute(sql, (status,))
            
            results = cursor.fetchall()
            connection.close()
            
            return results
            
        except Exception as e:
            print(f"❌ 상태별 검사 목록 조회 실패: {e}")
            return []
    
    def update_inspection_status(self, inspection_id: str, status: str, end_time: datetime = None) -> bool:
        """검사 상태 업데이트"""
        try:
            connection = self.connect()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            if end_time:
                sql = """
                UPDATE data_inspection_info 
                SET inspection_status = %s, end_time = %s, updated_at = NOW()
                WHERE inspection_id = %s
                """
                cursor.execute(sql, (status, end_time, inspection_id))
            else:
                sql = """
                UPDATE data_inspection_info 
                SET inspection_status = %s, updated_at = NOW()
                WHERE inspection_id = %s
                """
                cursor.execute(sql, (status, inspection_id))
            
            connection.commit()
            connection.close()
            
            print(f"✅ 검사 상태 업데이트 완료: {inspection_id} -> {status}")
            return True
            
        except Exception as e:
            print(f"❌ 검사 상태 업데이트 실패: {e}")
            return False

# 사용 예시
if __name__ == "__main__":
    service = DataInspectionService()
    
    # 검사 정보 저장 예시
    inspection_info = {
        'inspection_id': 'test_123',
        'table_name': 'tc_work_info',
        'data_source': 'TC',
        'total_rows': 67438,
        'total_columns': 20,
        'inspection_type': 'comprehensive',
        'inspection_status': 'completed',
        'start_time': datetime.now(),
        'end_time': datetime.now(),
        'processing_time_ms': 5000,
        'created_by': 'test_user'
    }
    
    service.save_inspection_info(inspection_info)
    
    # 최근 검사 목록 조회
    recent_inspections = service.get_recent_inspections(5)
    print(f"최근 검사: {len(recent_inspections)}개") 