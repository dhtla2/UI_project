import pandas as pd
import pymysql
import os
import numpy as np

def csv_to_mysql(csv_file='ais_data.csv', 
                host='localhost', 
                port=3307, 
                user='root', 
                password='Keti1234!', 
                database='port_database'):
    """
    CSV 파일을 MySQL 데이터베이스에 입력하는 함수
    """
    try:
        # CSV 파일 읽기
        print(f"CSV 파일 읽는 중: {csv_file}")
        df = pd.read_csv("/home/cotlab/UI_project/db/data_sample/"+csv_file, encoding='utf-8-sig')
        print(f"총 {len(df)}개의 레코드를 읽었습니다.")
        
        # NaN 값을 None으로 변환
        df = df.replace({np.nan: None})
        print("NaN 값을 NULL로 변환 완료")
        
        # MySQL 연결
        print("MySQL 데이터베이스에 연결 중...")
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        # 테이블이 없으면 생성
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS ais_info (
            id INT AUTO_INCREMENT PRIMARY KEY,
            mmsi_no VARCHAR(20),
            imo_no VARCHAR(20),
            vssl_nm VARCHAR(100),
            call_letter VARCHAR(20),
            vssl_tp VARCHAR(50),
            vssl_tp_cd VARCHAR(10),
            vssl_tp_crgo VARCHAR(50),
            vssl_cls VARCHAR(10),
            vssl_len DECIMAL(10,2),
            vssl_width DECIMAL(10,2),
            flag VARCHAR(50),
            flag_cd VARCHAR(10),
            vssl_def_brd DECIMAL(10,2),
            lon DECIMAL(15,8),
            lat DECIMAL(15,8),
            sog DECIMAL(10,2),
            cog DECIMAL(10,2),
            rot DECIMAL(10,2),
            head_side DECIMAL(10,2),
            vssl_navi VARCHAR(50),
            vssl_navi_cd VARCHAR(10),
            source VARCHAR(20),
            dt_pos_utc VARCHAR(20),
            dt_static_utc VARCHAR(20),
            vssl_tp_main VARCHAR(50),
            vssl_tp_sub VARCHAR(50),
            dst_nm VARCHAR(100),
            dst_cd VARCHAR(20),
            eta VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        print("테이블 생성 완료")
        
        # 기존 데이터 삭제 (선택사항)
        cursor.execute("DELETE FROM ais_info")
        print("기존 데이터 삭제 완료")
        
        # 데이터 삽입
        print("데이터 삽입 중...")
        insert_sql = """
        INSERT INTO ais_info (
            mmsi_no, imo_no, vssl_nm, call_letter, vssl_tp, vssl_tp_cd, vssl_tp_crgo, vssl_cls,
            vssl_len, vssl_width, flag, flag_cd, vssl_def_brd, lon, lat, sog, cog, rot, head_side,
            vssl_navi, vssl_navi_cd, source, dt_pos_utc, dt_static_utc, vssl_tp_main, vssl_tp_sub,
            dst_nm, dst_cd, eta
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # DataFrame을 리스트로 변환
        data_to_insert = []
        for _, row in df.iterrows():
            data_to_insert.append((
                row['mmsiNo'], row['imoNo'], row['vsslNm'], row['callLetter'], 
                row['vsslTp'], row['vsslTpCd'], row['vsslTpCrgo'], row['vsslCls'],
                row['vsslLen'], row['vsslWidth'], row['flag'], row['flagCd'], 
                row['vsslDefBrd'], row['lon'], row['lat'], row['sog'], row['cog'], 
                row['rot'], row['headSide'], row['vsslNavi'], row['vsslNaviCd'], 
                row['source'], row['dt_pos_utc'], row['dt_static_utc'], 
                row['vsslTpMain'], row['vsslTpSub'], row['dstNm'], row['dstCd'], row['eta']
            ))
        
        # 배치 삽입
        cursor.executemany(insert_sql, data_to_insert)
        conn.commit()
        
        print(f"총 {len(data_to_insert)}개의 레코드가 성공적으로 삽입되었습니다.")
        
        # 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM ais_info")
        count = cursor.fetchone()[0]
        print(f"데이터베이스에 저장된 총 레코드 수: {count}")
        
        # 샘플 데이터 확인
        cursor.execute("SELECT * FROM ais_info LIMIT 3")
        sample_data = cursor.fetchall()
        print("\n샘플 데이터:")
        for row in sample_data:
            print(row)
        
        conn.close()
        print("\nMySQL 연결이 종료되었습니다.")
        return True
        
    except Exception as e:
        print(f"오류 발생: {e}")
        return False

if __name__ == "__main__":
    print("=== CSV to MySQL 데이터 입력 도구 ===\n")
    
    # 사용자 입력 받기
    password = input("MySQL root 비밀번호 (없으면 Enter): ")
    if not password:
        password = ""
    
    # CSV 파일을 MySQL에 입력
    success = csv_to_mysql(password=password)
    
    if success:
        print("\n=== 데이터 입력 완료 ===")
        print("이제 MySQL에서 다음 명령어로 데이터를 확인할 수 있습니다:")
        print("USE ais_database;")
        print("SELECT COUNT(*) FROM ais_info;")
        print("SELECT * FROM ais_info LIMIT 5;")
    else:
        print("\n=== 데이터 입력 실패 ===")