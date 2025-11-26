# UI 데이터베이스 설정
UI_MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Keti1234!',  # MySQL 비밀번호를 여기에 입력하세요
    'database': 'ui_database',
    'charset': 'utf8mb4'
}

# UI 데이터베이스 생성 SQL
CREATE_UI_DATABASE_SQL = """
CREATE DATABASE IF NOT EXISTS ui_database
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
"""

# 사용자 페이지 방문(로그인) 로그 테이블 생성 SQL
CREATE_PAGE_VISITS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS page_visits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    page_name VARCHAR(100) NOT NULL,
    page_url VARCHAR(255) NOT NULL,
    login_status ENUM('login', 'logout', 'visit') DEFAULT 'visit',
    visit_duration INT,  -- 초 단위 (로그아웃 시에만 기록)
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100),
    ip_address VARCHAR(45),
    user_agent TEXT,
    referrer VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_login_status (login_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# API 호출 로그 테이블 생성 SQL (추후 업데이트 예정)
CREATE_API_CALLS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS api_calls (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    api_endpoint VARCHAR(255) NOT NULL,
    http_method VARCHAR(10) NOT NULL,
    request_data JSON,
    response_status INT,
    response_time_ms INT,  -- 응답 시간 (밀리초)
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100),
    ip_address VARCHAR(45),
    user_agent TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_api_endpoint (api_endpoint),
    INDEX idx_response_status (response_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""" 