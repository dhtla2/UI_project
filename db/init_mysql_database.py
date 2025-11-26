#!/usr/bin/env python3
"""
MySQL 데이터베이스 초기화 스크립트
데이터베이스와 테이블을 생성하고 CSV 데이터를 임포트합니다.
"""

import pymysql
import pandas as pd
from database_config import MYSQL_CONFIG, CREATE_DATABASE_SQL, CREATE_TABLE_SQL
import sys
import os

def create_database():
    """데이터베이스 생성"""
    try:
        # 데이터베이스 없이 연결
        connection = pymysql.connect(
            host=MYSQL_CONFIG['host'],
            port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            charset=MYSQL_CONFIG['charset']
        )
        
        cursor = connection.cursor()
        
        # 데이터베이스 생성
        cursor.execute(CREATE_DATABASE_SQL)
        print("데이터베이스 'port_database'가 생성되었습니다.")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"데이터베이스 생성 실패: {e}")
        return False

def create_table():
    """테이블 생성"""
    try:
        connection = pymysql.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        # 테이블 생성
        cursor.execute(CREATE_TABLE_SQL)
        print("테이블 'ais_info'가 생성되었습니다.")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"테이블 생성 실패: {e}")
        return False

def import_csv_data(csv_file_path):
    """CSV 데이터를 MySQL에 임포트"""
    try:
        # CSV 파일 읽기
        df = pd.read_csv(csv_file_path)
        print(f"CSV 파일 '{csv_file_path}'에서 {len(df)}개의 레코드를 읽었습니다.")
        
        df = df.astype(object).where(pd.notna(df), None)

        # 데이터베이스 연결
        connection = pymysql.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        # 데이터 삽입
        insert_sql = """
        INSERT INTO ais_info (
            mmsi_no, imo_no, vssl_nm, call_letter, vssl_tp, vssl_tp_cd, vssl_tp_crgo, vssl_cls,
            vssl_len, vssl_width, flag, flag_cd, vssl_def_brd, lon, lat, sog, cog, rot, head_side,
            vssl_navi, vssl_navi_cd, source, dt_pos_utc, dt_static_utc, vssl_tp_main, vssl_tp_sub,
            dst_nm, dst_cd, eta
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        # 데이터프레임을 튜플 리스트로 변환
        data_tuples = []
        for _, row in df.iterrows():
            data_tuple = (
                row.get('mmsi_no'),
                row.get('imo_no'),
                row.get('vssl_nm'),
                row.get('call_letter'),
                row.get('vssl_tp'),
                row.get('vssl_tp_cd'),
                row.get('vssl_tp_crgo'),
                row.get('vssl_cls'),
                row.get('vssl_len'),
                row.get('vssl_width'),
                row.get('flag'),
                row.get('flag_cd'),
                row.get('vssl_def_brd'),
                row.get('lon'),
                row.get('lat'),
                row.get('sog'),
                row.get('cog'),
                row.get('rot'),
                row.get('head_side'),
                row.get('vssl_navi'),
                row.get('vssl_navi_cd'),
                row.get('source'),
                row.get('dt_pos_utc'),
                row.get('dt_static_utc'),
                row.get('vssl_tp_main'),
                row.get('vssl_tp_sub'),
                row.get('dst_nm'),
                row.get('dst_cd'),
                row.get('eta')
            )
            data_tuples.append(data_tuple)
        
        # 배치 삽입
        cursor.executemany(insert_sql, data_tuples)
        connection.commit()
        
        print(f"{len(data_tuples)}개의 레코드가 성공적으로 임포트되었습니다.")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"CSV 데이터 임포트 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("MySQL 데이터베이스 초기화를 시작합니다...")
    
    # 1. 데이터베이스 생성
    if not create_database():
        print("데이터베이스 생성에 실패했습니다.")
        return
    
    # 2. 테이블 생성
    if not create_table():
        print("테이블 생성에 실패했습니다.")
        return
    
    # 3. CSV 데이터 임포트 (선택사항)
    csv_file = input("CSV 파일 경로를 입력하세요 (건너뛰려면 Enter): ").strip()
    if csv_file and os.path.exists(csv_file):
        if import_csv_data(csv_file):
            print("CSV 데이터 임포트가 완료되었습니다.")
        else:
            print("CSV 데이터 임포트에 실패했습니다.")
    else:
        print("CSV 파일이 지정되지 않았거나 존재하지 않습니다. 데이터베이스 초기화만 완료됩니다.")
    
    print("MySQL 데이터베이스 초기화가 완료되었습니다.")

if __name__ == "__main__":
    main() 