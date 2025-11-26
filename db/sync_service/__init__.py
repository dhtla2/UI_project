#!/usr/bin/env python3
"""
API 동기화 서비스 패키지

AIPC_v0.3의 모든 API 엔드포인트를 port_database에 동기화하는 서비스입니다.
"""

from .endpoint_mapper import endpoint_mapper
from .data_transformer import data_transformer
from .db_sync_manager import DBSyncManager
from .api_sync_service import api_sync_service
from .sync_scheduler import sync_scheduler

__all__ = [
    'endpoint_mapper',
    'data_transformer', 
    'DBSyncManager',
    'api_sync_service',
    'sync_scheduler'
]

__version__ = "1.0.0"
__author__ = "API Sync Service Team"
__description__ = "API 데이터를 port_database에 동기화하는 서비스"

# 패키지 정보
PACKAGE_INFO = {
    "name": "API Sync Service",
    "version": __version__,
    "description": __description__,
    "components": {
        "endpoint_mapper": "API 엔드포인트와 DB 테이블 매핑",
        "data_transformer": "API 응답 데이터 변환",
        "db_sync_manager": "DB 동기화 관리",
        "api_sync_service": "메인 API 동기화 서비스",
        "sync_scheduler": "동기화 스케줄링"
    },
    "supported_endpoints": 25,
    "supported_tables": 20,
    "database": "port_database (Port 3307)"
}
