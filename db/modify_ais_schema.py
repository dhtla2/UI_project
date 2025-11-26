#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIS 정보 테이블 스키마 수정 스크립트
lon, lat 컬럼을 더 넓은 범위로 확장하여 위치 데이터 범위 초과 문제 해결
"""

import pymysql
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'ais_schema_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def modify_ais_schema():
    """AIS 정보 테이블 스키마 수정"""
    try:
        # DB 연결
        logger.info("🔌 데이터베이스 연결 중...")
        conn = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='1234',
            database='port_database',
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        logger.info("✅ 데이터베이스 연결 성공")
        
        # 현재 ais_info 테이블 구조 확인
        logger.info("📋 현재 ais_info 테이블 구조 확인 중...")
        cursor.execute("DESCRIBE ais_info")
        current_schema = cursor.fetchall()
        
        logger.info("현재 ais_info 테이블 구조:")
        for row in current_schema:
            logger.info(f"  {row[0]}: {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
        
        # lon, lat 컬럼 수정
        logger.info("🔧 ais_info 테이블 스키마 수정 중...")
        
        # lon 컬럼을 DECIMAL(12,8)로 수정 (경도: -180 ~ +180)
        cursor.execute("ALTER TABLE ais_info MODIFY COLUMN lon DECIMAL(12,8)")
        logger.info("✅ lon 컬럼 수정 완료: DECIMAL(12,8)")
        
        # lat 컬럼을 DECIMAL(12,8)로 수정 (위도: -90 ~ +90)
        cursor.execute("ALTER TABLE ais_info MODIFY COLUMN lat DECIMAL(12,8)")
        logger.info("✅ lat 컬럼 수정 완료: DECIMAL(12,8)")
        
        # 변경사항 커밋
        conn.commit()
        logger.info("✅ 변경사항 커밋 완료")
        
        # 수정된 테이블 구조 확인
        logger.info("📋 수정된 ais_info 테이블 구조 확인 중...")
        cursor.execute("DESCRIBE ais_info")
        updated_schema = cursor.fetchall()
        
        logger.info("수정된 ais_info 테이블 구조:")
        for row in updated_schema:
            logger.info(f"  {row[0]}: {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
        
        # 테이블 정보 확인
        cursor.execute("SELECT COUNT(*) FROM ais_info")
        row_count = cursor.fetchone()[0]
        logger.info(f"📊 ais_info 테이블 레코드 수: {row_count:,}개")
        
        logger.info("🎉 AIS 테이블 스키마 수정 완료!")
        
    except Exception as e:
        logger.error(f"❌ 스키마 수정 실패: {e}")
        if 'conn' in locals():
            conn.rollback()
            logger.info("🔄 변경사항 롤백 완료")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            logger.info("🔌 데이터베이스 연결 해제")

if __name__ == "__main__":
    logger.info("🚀 AIS 테이블 스키마 수정 시작")
    logger.info("=" * 50)
    modify_ais_schema()
    logger.info("=" * 50)
    logger.info("🏁 AIS 테이블 스키마 수정 종료")
