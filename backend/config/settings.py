"""Application settings and configuration"""

import os
from typing import Optional

class Settings:
    """Application settings"""
    
    # Database settings
    db_host: str = "localhost"
    db_port: int = 3307
    db_user: str = "root"
    db_password: str = "Keti1234!"
    db_name: str = "port_database"
    db_charset: str = "utf8mb4"
    
    # AIS Database settings
    ais_db_path: str = "../ais_database.db"
    
    # API settings
    api_title: str = "Port Dashboard API"
    api_description: str = "API for Port Dashboard Application"
    api_version: str = "2.0.0"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 3000
    
    # CORS settings
    cors_origins: list = ["*"]
    
    # Logging settings
    log_level: str = "INFO"
    log_dir: str = "logs"
    
    # AIPC Client settings
    aipc_root: str = "/home/cotlab/AIPC_Client"
    aipc_project: str = "/home/cotlab/AIPC_Client/project_files"
    aipc_api_key: str = "w4v69kgnlu"
    aipc_base_url: str = "https://aipc-data.com/api"
    
    def __init__(self):
        # 환경변수에서 값 읽기
        self.db_host = os.getenv("DB_HOST", self.db_host)
        self.db_port = int(os.getenv("DB_PORT", self.db_port))
        self.db_user = os.getenv("DB_USER", self.db_user)
        self.db_password = os.getenv("DB_PASSWORD", self.db_password)
        self.db_name = os.getenv("DB_NAME", self.db_name)
        self.port = int(os.getenv("PORT", self.port))
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)

# Global settings instance
settings = Settings()

