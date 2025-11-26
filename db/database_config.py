# MySQL 데이터베이스 설정
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'root',
    'password': 'Keti1234!',  # ui_database_config.py와 동일한 비밀번호
    'database': 'port_database',
    'charset': 'utf8mb4'
}

# 데이터베이스 생성 SQL
CREATE_DATABASE_SQL = """
CREATE DATABASE IF NOT EXISTS port_database
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
"""

# AIS 정보 테이블 생성 SQL
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ais_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mmsi_no VARCHAR(20),
    imo_no VARCHAR(20),
    vssl_nm VARCHAR(100),
    call_letter VARCHAR(20),
    vssl_tp VARCHAR(50),
    vssl_tp_cd VARCHAR(10),
    vssl_tp_crgo VARCHAR(50),
    vssl_cls VARCHAR(20),
    vssl_len DECIMAL(10,2),
    vssl_width DECIMAL(10,2),
    flag VARCHAR(50),
    flag_cd VARCHAR(10),
    vssl_def_brd DECIMAL(10,2),
    lon DECIMAL(10,6),
    lat DECIMAL(10,6),
    sog DECIMAL(8,2),
    cog DECIMAL(8,2),
    rot DECIMAL(8,2),
    head_side DECIMAL(8,2),
    vssl_navi VARCHAR(50),
    vssl_navi_cd VARCHAR(10),
    source VARCHAR(50),
    dt_pos_utc DATETIME,
    dt_static_utc DATETIME,
    vssl_tp_main VARCHAR(50),
    vssl_tp_sub VARCHAR(50),
    dst_nm VARCHAR(100),
    dst_cd VARCHAR(20),
    eta VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""" 