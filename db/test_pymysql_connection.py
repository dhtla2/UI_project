#!/usr/bin/env python3
"""
PyMySQL 연결 테스트 스크립트
"""

import pymysql
from database_config import MYSQL_CONFIG

def test_connection():
    """데이터베이스 연결 테스트"""
    try:
        # 데이터베이스 없이 연결 시도
        connection = pymysql.connect(
            host=MYSQL_CONFIG['host'],
            port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            charset=MYSQL_CONFIG['charset']
        )
        
        print("✅ MariaDB 연결 성공!")
        
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"MariaDB 버전: {version[0]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        print("\n해결 방법:")
        print("1. MariaDB가 실행 중인지 확인: sudo systemctl status mariadb")
        print("2. MariaDB 시작: sudo systemctl start mariadb")
        print("3. 비밀번호 설정: sudo mysql -u root")
        print("4. database_config.py에서 비밀번호 확인")
        return False

if __name__ == "__main__":
    test_connection()