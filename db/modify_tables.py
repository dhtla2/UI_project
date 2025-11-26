#!/usr/bin/env python3
"""
테이블 구조 변경 스크립트
"""

import pymysql
from database_config import MYSQL_CONFIG

class TableModifier:
    """테이블 구조 변경 클래스"""
    
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
    
    def add_column(self, table_name: str, column_name: str, column_definition: str) -> bool:
        """컬럼 추가"""
        try:
            connection = self.connect()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
            cursor.execute(sql)
            
            connection.commit()
            connection.close()
            
            print(f"✅ 컬럼 추가 완료: {table_name}.{column_name}")
            return True
            
        except Exception as e:
            print(f"❌ 컬럼 추가 실패: {e}")
            return False
    
    def modify_column(self, table_name: str, column_name: str, new_definition: str) -> bool:
        """컬럼 수정"""
        try:
            connection = self.connect()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            sql = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} {new_definition}"
            cursor.execute(sql)
            
            connection.commit()
            connection.close()
            
            print(f"✅ 컬럼 수정 완료: {table_name}.{column_name}")
            return True
            
        except Exception as e:
            print(f"❌ 컬럼 수정 실패: {e}")
            return False
    
    def drop_column(self, table_name: str, column_name: str) -> bool:
        """컬럼 삭제"""
        try:
            connection = self.connect()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            sql = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
            cursor.execute(sql)
            
            connection.commit()
            connection.close()
            
            print(f"✅ 컬럼 삭제 완료: {table_name}.{column_name}")
            return True
            
        except Exception as e:
            print(f"❌ 컬럼 삭제 실패: {e}")
            return False
    
    def add_index(self, table_name: str, index_name: str, columns: str) -> bool:
        """인덱스 추가"""
        try:
            connection = self.connect()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            sql = f"ALTER TABLE {table_name} ADD INDEX {index_name} ({columns})"
            cursor.execute(sql)
            
            connection.commit()
            connection.close()
            
            print(f"✅ 인덱스 추가 완료: {table_name}.{index_name}")
            return True
            
        except Exception as e:
            print(f"❌ 인덱스 추가 실패: {e}")
            return False
    
    def show_table_structure(self, table_name: str):
        """테이블 구조 확인"""
        try:
            connection = self.connect()
            if not connection:
                return
            
            cursor = connection.cursor()
            
            sql = f"DESCRIBE {table_name}"
            cursor.execute(sql)
            
            columns = cursor.fetchall()
            
            print(f"\n📋 테이블 구조: {table_name}")
            print("-" * 80)
            print(f"{'Field':<20} {'Type':<20} {'Null':<10} {'Key':<10} {'Default':<15} {'Extra':<10}")
            print("-" * 80)
            
            for column in columns:
                print(f"{column[0]:<20} {column[1]:<20} {column[2]:<10} {column[3]:<10} {str(column[4]):<15} {column[5]:<10}")
            
            connection.close()
            
        except Exception as e:
            print(f"❌ 테이블 구조 확인 실패: {e}")
    
    def show_all_tables(self):
        """모든 테이블 목록 확인"""
        try:
            connection = self.connect()
            if not connection:
                return
            
            cursor = connection.cursor()
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print("\n📋 데이터베이스의 모든 테이블:")
            for table in tables:
                print(f"  - {table[0]}")
            
            connection.close()
            
        except Exception as e:
            print(f"❌ 테이블 목록 조회 실패: {e}")

def main():
    """메인 함수 - 테이블 구조 변경 예시"""
    modifier = TableModifier()
    
    print("🔧 테이블 구조 변경 도구")
    print("=" * 50)
    
    # 현재 테이블 목록 확인
    modifier.show_all_tables()
    
    # 예시: tc_work_info 테이블에 새 컬럼 추가
    print("\n📝 테이블 구조 변경 예시:")
    
    # 1. 현재 구조 확인
    modifier.show_table_structure("tc_work_info")
    
    # 2. 새 컬럼 추가 (예시)
    # modifier.add_column("tc_work_info", "priority", "INT DEFAULT 0")
    
    # 3. 컬럼 수정 (예시)
    # modifier.modify_column("tc_work_info", "wkTime", "DATETIME NULL")
    
    # 4. 인덱스 추가 (예시)
    # modifier.add_index("tc_work_info", "idx_priority", "priority")
    
    print("\n💡 사용법:")
    print("  - 컬럼 추가: modifier.add_column('테이블명', '컬럼명', '데이터타입')")
    print("  - 컬럼 수정: modifier.modify_column('테이블명', '컬럼명', '새데이터타입')")
    print("  - 컬럼 삭제: modifier.drop_column('테이블명', '컬럼명')")
    print("  - 인덱스 추가: modifier.add_index('테이블명', '인덱스명', '컬럼명')")

if __name__ == "__main__":
    main() 