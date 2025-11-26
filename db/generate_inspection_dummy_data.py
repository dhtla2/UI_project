#!/usr/bin/env python3
"""
검사 히스토리 더미 데이터 생성 스크립트

10월 1일부터 14일까지의 검사 히스토리 더미 데이터를 생성합니다.
- AIS, TOS, TC, QC 각 시스템별 검사 결과 생성
- 완전성(completeness), 유효성(validity) 검사 결과 생성
- 현실적인 통과율과 실패율 적용

사용법:
    python generate_inspection_dummy_data.py
"""

import pymysql
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from database_config import MYSQL_CONFIG

class InspectionDummyDataGenerator:
    """검사 더미 데이터 생성기"""
    
    def __init__(self):
        self.config = MYSQL_CONFIG.copy()
        
        # 검사 대상 시스템
        self.systems = {
            'ais': {
                'name': 'AIS',
                'inspection_pattern': 'ais_info_inspection',
                'completeness_fields': [
                    'mmsi_no', 'imo_no', 'vssl_nm', 'call_letter', 'vssl_tp',
                    'flag', 'lon', 'lat', 'sog', 'cog', 'dt_pos_utc'
                ],
                'validity_checks': [
                    'longitude_range', 'latitude_range', 'speed_range', 
                    'grid_validation', 'timestamp_format'
                ]
            },
            'tos': {
                'name': 'TOS',
                'inspection_pattern': 'berth',
                'completeness_fields': [
                    'berth_schedule_id', 'terminal_id', 'berth_id', 'vessel_name',
                    'arrival_time', 'departure_time', 'berth_status'
                ],
                'validity_checks': [
                    'date_range', 'terminal_code', 'berth_code', 'status_code'
                ]
            },
            'tc': {
                'name': 'TC',
                'inspection_pattern': 'tc_work',
                'completeness_fields': [
                    'work_id', 'terminal_id', 'container_no', 'work_type',
                    'work_time', 'operator_id'
                ],
                'validity_checks': [
                    'container_format', 'work_type_code', 'time_validation'
                ]
            },
            'qc': {
                'name': 'QC',
                'inspection_pattern': 'qc_work',
                'completeness_fields': [
                    'inspection_id', 'container_no', 'inspection_type',
                    'inspection_result', 'inspector_id', 'inspection_time'
                ],
                'validity_checks': [
                    'result_code', 'inspection_type_code', 'time_validation'
                ]
            }
        }
    
    def connect(self):
        """데이터베이스 연결"""
        try:
            connection = pymysql.connect(**self.config)
            return connection
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            return None
    
    def generate_inspection_results(
        self, 
        system_key: str, 
        date: datetime
    ) -> List[Dict[str, Any]]:
        """특정 시스템, 날짜에 대한 검사 결과 생성"""
        
        system = self.systems[system_key]
        results = []
        
        # 완전성 검사 결과 생성
        for field in system['completeness_fields']:
            # 80-95% 확률로 PASS
            status = 'PASS' if random.random() < 0.88 else 'FAIL'
            affected_rows = 0 if status == 'PASS' else random.randint(1, 20)
            
            result = {
                'inspection_id': f"{system['inspection_pattern']}_{date.strftime('%Y%m%d')}",
                'check_type': 'completeness',
                'check_name': f'{field}_completeness',
                'message': f'{field} 필드 완전성 검사' + (' 통과' if status == 'PASS' else f' 실패 ({affected_rows}건 누락)'),
                'status': status,
                'severity': 'LOW' if status == 'PASS' else 'MEDIUM',
                'affected_rows': affected_rows,
                'affected_columns': field if status == 'FAIL' else None,
                'details': None,
                'created_at': date + timedelta(hours=random.randint(8, 20), minutes=random.randint(0, 59))
            }
            results.append(result)
        
        # 유효성 검사 결과 생성
        for check in system['validity_checks']:
            # 85-98% 확률로 PASS
            status = 'PASS' if random.random() < 0.92 else 'FAIL'
            affected_rows = 0 if status == 'PASS' else random.randint(1, 15)
            
            result = {
                'inspection_id': f"{system['inspection_pattern']}_{date.strftime('%Y%m%d')}",
                'check_type': 'validity',
                'check_name': f'{check}_validation',
                'message': f'{check} 유효성 검사' + (' 통과' if status == 'PASS' else f' 실패 ({affected_rows}건 오류)'),
                'status': status,
                'severity': 'LOW' if status == 'PASS' else 'HIGH' if affected_rows > 10 else 'MEDIUM',
                'affected_rows': affected_rows,
                'affected_columns': None,
                'details': None,
                'created_at': date + timedelta(hours=random.randint(8, 20), minutes=random.randint(0, 59))
            }
            results.append(result)
        
        return results
    
    def insert_inspection_results(self, results: List[Dict[str, Any]]) -> bool:
        """검사 결과를 데이터베이스에 삽입"""
        try:
            connection = self.connect()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            # Foreign key 체크 일시 비활성화
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            
            sql = """
            INSERT INTO data_inspection_results (
                inspection_id, check_type, check_name, message, status, 
                severity, affected_rows, affected_columns, details, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            inserted_count = 0
            for result in results:
                try:
                    values = (
                        result['inspection_id'],
                        result['check_type'],
                        result['check_name'],
                        result['message'],
                        result['status'],
                        result['severity'],
                        result['affected_rows'],
                        result['affected_columns'],
                        result['details'],
                        result['created_at']
                    )
                    cursor.execute(sql, values)
                    inserted_count += 1
                except Exception as e:
                    print(f"⚠️  레코드 삽입 실패: {e}")
                    continue
            
            # Foreign key 체크 재활성화
            cursor.execute("SET FOREIGN_KEY_CHECKS=1")
            
            connection.commit()
            connection.close()
            
            print(f"✅ {inserted_count}개 검사 결과 삽입 완료")
            return True
            
        except Exception as e:
            print(f"❌ 검사 결과 삽입 실패: {e}")
            return False
    
    def check_existing_data(self, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """기존 데이터 확인"""
        try:
            connection = self.connect()
            if not connection:
                return {}
            
            cursor = connection.cursor()
            
            sql = """
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM data_inspection_results
            WHERE DATE(created_at) BETWEEN %s AND %s
            GROUP BY DATE(created_at)
            """
            
            cursor.execute(sql, (start_date.date(), end_date.date()))
            results = cursor.fetchall()
            
            connection.close()
            
            existing_data = {str(row[0]): row[1] for row in results}
            return existing_data
            
        except Exception as e:
            print(f"❌ 기존 데이터 확인 실패: {e}")
            return {}
    
    def generate_all_dummy_data(
        self, 
        start_date: datetime, 
        end_date: datetime,
        force: bool = False
    ):
        """모든 시스템에 대해 지정된 기간의 더미 데이터 생성"""
        
        print(f"\n{'='*80}")
        print(f"🔍 검사 히스토리 더미 데이터 생성기")
        print(f"{'='*80}")
        print(f"📅 기간: {start_date.date()} ~ {end_date.date()}")
        print(f"🖥️  시스템: {', '.join([s['name'] for s in self.systems.values()])}")
        print(f"{'='*80}\n")
        
        # 기존 데이터 확인
        if not force:
            existing_data = self.check_existing_data(start_date, end_date)
            if existing_data:
                print("⚠️  해당 기간에 이미 데이터가 존재합니다:")
                for date, count in existing_data.items():
                    print(f"   📅 {date}: {count}건")
                
                response = input("\n계속 진행하시겠습니까? (y/N): ")
                if response.lower() != 'y':
                    print("❌ 작업이 취소되었습니다.")
                    return
                print()
        
        # 날짜별로 데이터 생성
        current_date = start_date
        total_inserted = 0
        
        while current_date <= end_date:
            print(f"📅 {current_date.date()} 데이터 생성 중...")
            
            all_results = []
            
            # 각 시스템별 검사 결과 생성
            for system_key in self.systems.keys():
                system_results = self.generate_inspection_results(system_key, current_date)
                all_results.extend(system_results)
                print(f"   ✅ {self.systems[system_key]['name']}: {len(system_results)}건")
            
            # 데이터베이스에 삽입
            if self.insert_inspection_results(all_results):
                total_inserted += len(all_results)
            
            print()
            current_date += timedelta(days=1)
        
        print(f"{'='*80}")
        print(f"🎉 작업 완료!")
        print(f"📊 총 {total_inserted}건의 검사 결과가 생성되었습니다.")
        print(f"{'='*80}\n")
    
    def delete_data_in_range(self, start_date: datetime, end_date: datetime):
        """지정된 기간의 데이터 삭제 (재생성을 위해)"""
        try:
            connection = self.connect()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            sql = """
            DELETE FROM data_inspection_results
            WHERE DATE(created_at) BETWEEN %s AND %s
            """
            
            cursor.execute(sql, (start_date.date(), end_date.date()))
            deleted_count = cursor.rowcount
            
            connection.commit()
            connection.close()
            
            print(f"✅ {deleted_count}건의 기존 데이터를 삭제했습니다.")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 삭제 실패: {e}")
            return False


def main():
    """메인 함수"""
    import sys
    
    generator = InspectionDummyDataGenerator()
    
    # 기본 날짜: 2025년 10월 1일 ~ 14일
    start_date = datetime(2025, 10, 1)
    end_date = datetime(2025, 10, 14)
    
    # 명령행 인수 처리
    if len(sys.argv) > 1:
        if sys.argv[1] == '--delete':
            print("⚠️  지정된 기간의 데이터를 삭제합니다...")
            generator.delete_data_in_range(start_date, end_date)
            return
        elif sys.argv[1] == '--force':
            # 강제 모드: 기존 데이터 체크 없이 생성
            generator.generate_all_dummy_data(start_date, end_date, force=True)
            return
        elif sys.argv[1] == '--help':
            print("""
사용법:
    python generate_inspection_dummy_data.py [옵션]

옵션:
    (없음)      기본 모드 - 10월 1일~14일 데이터 생성 (기존 데이터 확인)
    --force     강제 모드 - 기존 데이터 확인 없이 생성
    --delete    삭제 모드 - 10월 1일~14일 데이터 삭제
    --help      도움말 표시
            """)
            return
    
    # 기본 모드: 데이터 생성
    generator.generate_all_dummy_data(start_date, end_date)


if __name__ == "__main__":
    main()

