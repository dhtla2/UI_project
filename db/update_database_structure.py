#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DB 구조 업데이트 스크립트
API 응답 결과 기반으로 DB 테이블 구조를 업데이트합니다.
"""

import pymysql
import logging
import sys
import os
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'db_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# DB 설정
DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'root',
    'password': 'Keti1234!',
    'database': 'port_database',
    'charset': 'utf8mb4'
}

def create_connection():
    """데이터베이스 연결 생성"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        logger.info("✅ 데이터베이스 연결 성공")
        return connection
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 실패: {e}")
        return None

def execute_sql_file(connection, sql_file_path):
    """SQL 파일 실행"""
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # SQL 문을 세미콜론으로 분리
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        cursor = connection.cursor()
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(sql_statements, 1):
            if not statement or statement.startswith('--'):
                continue
                
            try:
                cursor.execute(statement)
                logger.info(f"✅ SQL 실행 성공 ({i}/{len(sql_statements)}): {statement[:50]}...")
                success_count += 1
            except Exception as e:
                logger.error(f"❌ SQL 실행 실패 ({i}/{len(sql_statements)}): {e}")
                logger.error(f"   SQL: {statement[:100]}...")
                error_count += 1
        
        connection.commit()
        cursor.close()
        
        logger.info(f"📊 SQL 실행 완료: 성공 {success_count}건, 실패 {error_count}건")
        return success_count, error_count
        
    except Exception as e:
        logger.error(f"❌ SQL 파일 실행 중 오류: {e}")
        return 0, 0

def check_table_structure(connection):
    """테이블 구조 확인"""
    try:
        cursor = connection.cursor()
        
        # 테이블 목록 조회
        cursor.execute("""
            SELECT table_name, table_rows, data_length, index_length
            FROM information_schema.tables 
            WHERE table_schema = 'port_database'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        
        logger.info("📋 현재 DB 테이블 구조:")
        logger.info("-" * 80)
        logger.info(f"{'테이블명':<25} {'레코드수':<10} {'데이터크기':<12} {'인덱스크기':<12}")
        logger.info("-" * 80)
        
        total_tables = 0
        total_rows = 0
        
        for table_name, table_rows, data_length, index_length in tables:
            if table_rows is None:
                table_rows = 0
            if data_length is None:
                data_length = 0
            if index_length is None:
                index_length = 0
                
            logger.info(f"{table_name:<25} {table_rows:<10} {data_length:<12} {index_length:<12}")
            total_tables += 1
            total_rows += table_rows
        
        logger.info("-" * 80)
        logger.info(f"총 테이블 수: {total_tables}개")
        logger.info(f"총 레코드 수: {total_rows:,}건")
        
        cursor.close()
        return total_tables, total_rows
        
    except Exception as e:
        logger.error(f"❌ 테이블 구조 확인 중 오류: {e}")
        return 0, 0

def backup_existing_tables(connection):
    """기존 테이블 백업"""
    try:
        cursor = connection.cursor()
        
        # 백업할 테이블 목록
        backup_tables = [
            'ais_info', 'cntr_load_unload_info', 'cntr_report_detail',
            'vssl_entr_report', 'vssl_dprt_report', 'vssl_history',
            'vssl_pass_report', 'cargo_imp_exp_report', 'cargo_item_code',
            'dg_imp_report', 'dg_manifest', 'fac_use_statement',
            'fac_use_stmt_bill', 'vssl_sec_isps_info', 'vssl_sec_port_info',
            'load_unload_from_to_info', 'vssl_sanction_info', 'country_code',
            'vssl_entr_intn_code', 'pa_code', 'port_code'
        ]
        
        backup_count = 0
        
        for table_name in backup_tables:
            try:
                # 백업 테이블명 생성
                backup_table_name = f"{table_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # 테이블 존재 여부 확인
                cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                if cursor.fetchone():
                    # 테이블 백업
                    cursor.execute(f"CREATE TABLE {backup_table_name} AS SELECT * FROM {table_name}")
                    logger.info(f"✅ {table_name} 테이블 백업 완료: {backup_table_name}")
                    backup_count += 1
                else:
                    logger.info(f"ℹ️ {table_name} 테이블이 존재하지 않음 (백업 생략)")
                    
            except Exception as e:
                logger.warning(f"⚠️ {table_name} 테이블 백업 실패: {e}")
        
        connection.commit()
        cursor.close()
        
        logger.info(f"📦 테이블 백업 완료: {backup_count}개 테이블")
        return backup_count
        
    except Exception as e:
        logger.error(f"❌ 테이블 백업 중 오류: {e}")
        return 0

def main():
    """메인 실행 함수"""
    logger.info("🚀 DB 구조 업데이트 시작")
    logger.info("=" * 60)
    
    # 1. 데이터베이스 연결
    connection = create_connection()
    if not connection:
        logger.error("❌ 데이터베이스 연결 실패로 종료")
        return
    
    try:
        # 2. 현재 테이블 구조 확인
        logger.info("📋 현재 DB 구조 확인 중...")
        current_tables, current_rows = check_table_structure(connection)
        
        # 3. 기존 테이블 백업
        logger.info("📦 기존 테이블 백업 중...")
        backup_count = backup_existing_tables(connection)
        
        # 4. 새로운 스키마 실행
        logger.info("🔧 새로운 DB 스키마 적용 중...")
        sql_file_path = "updated_database_schema.sql"
        
        if not os.path.exists(sql_file_path):
            logger.error(f"❌ SQL 파일을 찾을 수 없음: {sql_file_path}")
            return
        
        success_count, error_count = execute_sql_file(connection, sql_file_path)
        
        # 5. 업데이트된 테이블 구조 확인
        logger.info("📋 업데이트된 DB 구조 확인 중...")
        updated_tables, updated_rows = check_table_structure(connection)
        
        # 6. 결과 요약
        logger.info("=" * 60)
        logger.info("🎉 DB 구조 업데이트 완료!")
        logger.info(f"📊 백업된 테이블: {backup_count}개")
        logger.info(f"📊 SQL 실행 결과: 성공 {success_count}건, 실패 {error_count}건")
        logger.info(f"📊 테이블 수 변화: {current_tables}개 → {updated_tables}개")
        logger.info(f"📊 레코드 수 변화: {current_rows:,}건 → {updated_rows:,}건")
        
        if error_count == 0:
            logger.info("✅ 모든 테이블이 성공적으로 업데이트되었습니다!")
        else:
            logger.warning(f"⚠️ {error_count}개의 SQL 실행이 실패했습니다. 로그를 확인하세요.")
        
    except Exception as e:
        logger.error(f"❌ DB 구조 업데이트 중 오류: {e}")
        
    finally:
        connection.close()
        logger.info("🔌 데이터베이스 연결 종료")

if __name__ == "__main__":
    main()
