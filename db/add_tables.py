#!/usr/bin/env python3
"""
기존 데이터베이스에 새로운 테이블을 추가하는 스크립트
"""

import pymysql
from database_config import MYSQL_CONFIG
import sys

# TC 작업 정보 테이블 생성 SQL
CREATE_TC_WORK_INFO_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS tc_work_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tmnlId VARCHAR(20) NOT NULL,
    shpCd VARCHAR(20),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    tcNo VARCHAR(20),
    cntrNo VARCHAR(20),
    tmnlNm VARCHAR(100),
    shpNm VARCHAR(100),
    wkId VARCHAR(50),
    jobNo VARCHAR(50),
    szTp VARCHAR(20),
    ytNo VARCHAR(20),
    rtNo VARCHAR(20),
    block VARCHAR(20),
    bay VARCHAR(10),
    roww VARCHAR(10),
    ordTime DATETIME,
    wkTime DATETIME,
    jobState VARCHAR(50),
    evntTime DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tmnlId (tmnlId),
    INDEX idx_cntrNo (cntrNo),
    INDEX idx_tcNo (tcNo),
    INDEX idx_wkTime (wkTime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# QC 작업 정보 테이블 생성 SQL
CREATE_QC_WORK_INFO_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS qc_work_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tmnlId VARCHAR(20) NOT NULL,
    shpCd VARCHAR(20),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    qcNo VARCHAR(20),
    cntrNo VARCHAR(20),
    tmnlNm VARCHAR(100),
    shpNm VARCHAR(100),
    wkId VARCHAR(50),
    jobNo VARCHAR(50),
    szTp VARCHAR(20),
    ytNo VARCHAR(20),
    rtNo VARCHAR(20),
    block VARCHAR(20),
    bay VARCHAR(10),
    roww VARCHAR(10),
    ordTime DATETIME,
    wkTime DATETIME,
    jobState VARCHAR(50),
    evntTime DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tmnlId (tmnlId),
    INDEX idx_cntrNo (cntrNo),
    INDEX idx_qcNo (qcNo),
    INDEX idx_wkTime (wkTime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# YT 작업 정보 테이블 생성 SQL
CREATE_YT_WORK_INFO_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS yt_work_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tmnlId VARCHAR(20) NOT NULL,
    shpCd VARCHAR(20),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    ytNo VARCHAR(20),
    cntrNo VARCHAR(20),
    tmnlNm VARCHAR(100),
    shpNm VARCHAR(100),
    wkId VARCHAR(50),
    jobNo VARCHAR(50),
    szTp VARCHAR(20),
    rtNo VARCHAR(20),
    block VARCHAR(20),
    bay VARCHAR(10),
    roww VARCHAR(10),
    ordTime DATETIME,
    wkTime DATETIME,
    jobState VARCHAR(50),
    evntTime DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tmnlId (tmnlId),
    INDEX idx_cntrNo (cntrNo),
    INDEX idx_ytNo (ytNo),
    INDEX idx_wkTime (wkTime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# 선석 계획 테이블 생성 SQL
CREATE_BERTH_SCHEDULE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS berth_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tmnlId VARCHAR(20) NOT NULL,
    shpCd VARCHAR(20),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    berthNo VARCHAR(20),
    cntrNo VARCHAR(20),
    tmnlNm VARCHAR(100),
    shpNm VARCHAR(100),
    ata DATETIME,
    atd DATETIME,
    eta DATETIME,
    etd DATETIME,
    berthState VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tmnlId (tmnlId),
    INDEX idx_cntrNo (cntrNo),
    INDEX idx_berthNo (berthNo),
    INDEX idx_ata (ata),
    INDEX idx_atd (atd)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# 데이터 검사 정보 테이블 생성 SQL
CREATE_DATA_INSPECTION_INFO_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS data_inspection_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100) UNIQUE NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    data_source VARCHAR(50) NOT NULL,  -- 'TC', 'QC', 'YT', 'BERTH', 'AIS' 등
    total_rows INT NOT NULL,
    total_columns INT NOT NULL,
    inspection_type VARCHAR(50) NOT NULL,  -- 'comprehensive', 'range', 'duplicate', 'usage' 등
    inspection_status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    start_time DATETIME,
    end_time DATETIME,
    processing_time_ms INT,  -- 처리 시간 (밀리초)
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_table_name (table_name),
    INDEX idx_data_source (data_source),
    INDEX idx_inspection_status (inspection_status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# 데이터 검사 결과 상세 테이블 생성 SQL
CREATE_DATA_INSPECTION_RESULTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS data_inspection_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100) NOT NULL,
    check_type VARCHAR(50) NOT NULL,  -- 'DV', 'DC', 'DU' 등
    check_name VARCHAR(100) NOT NULL,  -- 'RANGE', 'DUPLICATE', 'USAGE' 등
    message TEXT NOT NULL,
    status ENUM('PASS', 'FAIL', 'WARNING', 'ERROR') NOT NULL,
    severity ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') DEFAULT 'MEDIUM',
    affected_rows INT DEFAULT 0,
    affected_columns JSON,  -- 영향을 받은 컬럼들
    details JSON,  -- 상세 정보 (범위, 중복값 등)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspection_id) REFERENCES data_inspection_info(inspection_id) ON DELETE CASCADE,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_check_type (check_type),
    INDEX idx_status (status),
    INDEX idx_severity (severity),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# 데이터 검사 요약 테이블 생성 SQL
CREATE_DATA_INSPECTION_SUMMARY_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS data_inspection_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100) UNIQUE NOT NULL,
    total_checks INT NOT NULL,
    passed_checks INT NOT NULL,
    failed_checks INT NOT NULL,
    warning_checks INT NOT NULL,
    error_checks INT NOT NULL,
    pass_rate DECIMAL(5,2),  -- 통과율 (%)
    data_quality_score DECIMAL(5,2),  -- 데이터 품질 점수 (0-100)
    summary_json JSON,  -- 전체 요약 정보
    recommendations TEXT,  -- 개선 권장사항
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspection_id) REFERENCES data_inspection_info(inspection_id) ON DELETE CASCADE,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_pass_rate (pass_rate),
    INDEX idx_data_quality_score (data_quality_score),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# API 조회 파라미터 및 검사 시간 테이블 생성 SQL
CREATE_API_CALL_INFO_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS api_call_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100) NOT NULL,
    api_endpoint VARCHAR(255) NOT NULL,
    request_params JSON NOT NULL,  -- API 요청 파라미터
    request_headers JSON,  -- API 요청 헤더
    response_status_code INT,
    response_time_ms INT,  -- API 응답 시간 (밀리초)
    data_retrieval_start_time DATETIME,
    data_retrieval_end_time DATETIME,
    data_retrieval_duration_ms INT,  -- 데이터 조회 소요 시간
    total_records_retrieved INT,  -- 조회된 총 레코드 수
    data_file_path VARCHAR(500),  -- 저장된 CSV 파일 경로
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspection_id) REFERENCES data_inspection_info(inspection_id) ON DELETE CASCADE,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_api_endpoint (api_endpoint),
    INDEX idx_data_retrieval_start_time (data_retrieval_start_time),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# API 응답 데이터 저장 테이블 생성 SQL
CREATE_API_RESPONSE_DATA_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS api_response_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100) NOT NULL,
    data_source VARCHAR(50) NOT NULL,  -- 'TC', 'QC', 'YT', 'BERTH' 등
    data_type VARCHAR(50) NOT NULL,  -- 'work_info', 'schedule' 등
    raw_response_data JSON,  -- 원본 응답 데이터 (선택사항)
    processed_data_count INT,  -- 처리된 데이터 수
    data_columns JSON,  -- 데이터 컬럼 정보
    data_file_name VARCHAR(255),  -- 저장된 파일명
    data_file_size_bytes BIGINT,  -- 파일 크기 (바이트)
    data_checksum VARCHAR(64),  -- 파일 체크섬 (MD5)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspection_id) REFERENCES data_inspection_info(inspection_id) ON DELETE CASCADE,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_data_source (data_source),
    INDEX idx_data_type (data_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

def add_table(table_name, create_sql):
    """테이블 추가"""
    try:
        connection = pymysql.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        # 테이블 생성
        cursor.execute(create_sql)
        print(f"✅ 테이블 '{table_name}'이 성공적으로 생성되었습니다.")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 테이블 '{table_name}' 생성 실패: {e}")
        return False

def check_table_exists(table_name):
    """테이블 존재 여부 확인"""
    try:
        connection = pymysql.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        # 테이블 존재 여부 확인
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        exists = cursor.fetchone() is not None
        
        connection.close()
        return exists
        
    except Exception as e:
        print(f"❌ 테이블 존재 여부 확인 실패: {e}")
        return False

def show_all_tables():
    """모든 테이블 목록 표시"""
    try:
        connection = pymysql.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print("\n📋 현재 데이터베이스의 테이블 목록:")
        for table in tables:
            print(f"  - {table[0]}")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ 테이블 목록 조회 실패: {e}")

def main():
    """메인 함수"""
    print("🚀 포트 데이터베이스에 테이블 추가")
    print("=" * 50)
    
    # 현재 테이블 목록 표시
    show_all_tables()
    
    # 추가할 테이블들
    tables_to_add = [
        # 작업 정보 테이블들
        ("tc_work_info", CREATE_TC_WORK_INFO_TABLE_SQL),
        ("qc_work_info", CREATE_QC_WORK_INFO_TABLE_SQL),
        ("yt_work_info", CREATE_YT_WORK_INFO_TABLE_SQL),
        ("berth_schedule", CREATE_BERTH_SCHEDULE_TABLE_SQL),
        
        # 데이터 검사 관련 테이블들
        ("data_inspection_info", CREATE_DATA_INSPECTION_INFO_TABLE_SQL),
        ("data_inspection_results", CREATE_DATA_INSPECTION_RESULTS_TABLE_SQL),
        ("data_inspection_summary", CREATE_DATA_INSPECTION_SUMMARY_TABLE_SQL),
        
        # API 호출 및 응답 데이터 관련 테이블들
        ("api_call_info", CREATE_API_CALL_INFO_TABLE_SQL),
        ("api_response_data", CREATE_API_RESPONSE_DATA_TABLE_SQL)
    ]
    
    print("\n📝 테이블 추가 시작...")
    
    for table_name, create_sql in tables_to_add:
        if check_table_exists(table_name):
            print(f"⚠️ 테이블 '{table_name}'이 이미 존재합니다.")
        else:
            add_table(table_name, create_sql)
    
    print("\n📋 최종 테이블 목록:")
    show_all_tables()
    
    print("\n✅ 테이블 추가 완료!")

if __name__ == "__main__":
    main() 