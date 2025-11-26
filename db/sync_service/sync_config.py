#!/usr/bin/env python3
"""
동기화 서비스 설정 파일

API 동기화 서비스의 모든 설정을 중앙에서 관리합니다.
"""

import os
from typing import Dict, Any

# 기본 설정
DEFAULT_CONFIG = {
    # 데이터베이스 설정
    "database": {
        "host": "localhost",
        "port": 3307,
        "user": "root",
        "password": "Keti1234!",
        "database": "port_database",
        "charset": "utf8mb4",
        "autocommit": True,
        "connect_timeout": 30,
        "read_timeout": 30,
        "write_timeout": 30
    },
    
    # API 서버 설정
    "api_server": {
        "base_url": "http://localhost:8000",
        "timeout": 30,
        "retry_count": 3,
        "retry_delay": 5
    },
    
    # 동기화 설정
    "sync": {
        "batch_size": 1000,           # 배치 처리 크기
        "max_concurrent": 5,          # 최대 동시 동기화 수
        "sync_timeout": 300,          # 동기화 타임아웃 (초)
        "enable_logging": True,       # 로깅 활성화
        "log_level": "INFO",          # 로그 레벨
        "log_file": "sync_service.log" # 로그 파일명
    },
    
    # 스케줄러 설정
    "scheduler": {
        "enable_auto_start": True,    # 자동 시작 활성화
        "check_interval": 1,          # 체크 간격 (초)
        "max_history": 1000,          # 최대 히스토리 수
        "enable_cleanup": True,       # 자동 정리 활성화
        "cleanup_days": 30            # 정리 기준 일수
    },
    
    # 우선순위별 동기화 간격 (초)
    "sync_intervals": {
        "high": 3600,      # 1시간
        "medium": 7200,    # 2시간
        "low": 21600       # 6시간
    },
    
    # 카테고리별 동기화 설정
    "category_config": {
        "work_info": {
            "priority": "high",
            "sync_interval": 3600,
            "description": "작업 정보 (TC, QC, YT)"
        },
        "schedule": {
            "priority": "high",
            "sync_interval": 1800,
            "description": "선석 계획"
        },
        "vessel_info": {
            "priority": "high",
            "sync_interval": 900,
            "description": "선박 정보 (AIS, 관제)"
        },
        "container": {
            "priority": "medium",
            "sync_interval": 7200,
            "description": "컨테이너 정보"
        },
        "vessel_report": {
            "priority": "medium",
            "sync_interval": 3600,
            "description": "선박 신고 정보"
        },
        "cargo": {
            "priority": "medium",
            "sync_interval": 7200,
            "description": "화물 정보"
        },
        "dangerous_goods": {
            "priority": "high",
            "sync_interval": 1800,
            "description": "위험물 정보"
        },
        "facility": {
            "priority": "medium",
            "sync_interval": 7200,
            "description": "항만시설 정보"
        },
        "security": {
            "priority": "medium",
            "sync_interval": 14400,
            "description": "보안 정보"
        },
        "code": {
            "priority": "low",
            "sync_interval": 604800,
            "description": "코드 정보"
        }
    },
    
    # 로깅 설정
    "logging": {
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "file_rotation": "daily",
        "max_file_size": "10MB",
        "backup_count": 7
    },
    
    # 성능 모니터링 설정
    "monitoring": {
        "enable_metrics": True,       # 메트릭 수집 활성화
        "metrics_interval": 60,       # 메트릭 수집 간격 (초)
        "performance_threshold": {    # 성능 임계값
            "api_response_time": 5000,    # API 응답 시간 (ms)
            "db_insert_time": 1000,       # DB 삽입 시간 (ms)
            "sync_total_time": 30000      # 전체 동기화 시간 (ms)
        }
    }
}

class SyncConfig:
    """동기화 서비스 설정 관리"""
    
    def __init__(self, config_file: str = None):
        self.config = DEFAULT_CONFIG.copy()
        self.config_file = config_file
        
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
    
    def load_config(self, config_file: str) -> bool:
        """설정 파일 로드"""
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
            
            # 설정 병합
            self._merge_config(self.config, file_config)
            self.config_file = config_file
            
            return True
            
        except Exception as e:
            print(f"⚠️ 설정 파일 로드 실패: {e}")
            return False
    
    def _merge_config(self, base_config: Dict[str, Any], 
                     new_config: Dict[str, Any]):
        """설정 병합 (재귀적)"""
        for key, value in new_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value
    
    def save_config(self, config_file: str = None) -> bool:
        """설정 파일 저장"""
        try:
            import json
            target_file = config_file or self.config_file
            
            if not target_file:
                print("❌ 저장할 설정 파일 경로가 지정되지 않았습니다")
                return False
            
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"❌ 설정 파일 저장 실패: {e}")
            return False
    
    def get(self, key_path: str, default=None):
        """설정 값 조회 (점 표기법 지원)"""
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                value = value[key]
            
            return value
            
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value):
        """설정 값 설정 (점 표기법 지원)"""
        try:
            keys = key_path.split('.')
            config = self.config
            
            # 마지막 키까지 탐색
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # 마지막 키에 값 설정
            config[keys[-1]] = value
            
            return True
            
        except Exception as e:
            print(f"❌ 설정 값 설정 실패: {e}")
            return False
    
    def get_database_config(self) -> Dict[str, Any]:
        """데이터베이스 설정 반환"""
        return self.config.get("database", {})
    
    def get_api_server_config(self) -> Dict[str, Any]:
        """API 서버 설정 반환"""
        return self.config.get("api_server", {})
    
    def get_sync_config(self) -> Dict[str, Any]:
        """동기화 설정 반환"""
        return self.config.get("sync", {})
    
    def get_scheduler_config(self) -> Dict[str, Any]:
        """스케줄러 설정 반환"""
        return self.config.get("scheduler", {})
    
    def get_category_config(self) -> Dict[str, Any]:
        """카테고리별 설정 반환"""
        return self.config.get("category_config", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """로깅 설정 반환"""
        return self.config.get("logging", {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """모니터링 설정 반환"""
        return self.config.get("monitoring", {})
    
    def validate_config(self) -> bool:
        """설정 유효성 검증"""
        try:
            required_keys = [
                "database.host",
                "database.port",
                "database.database",
                "api_server.base_url"
            ]
            
            for key in required_keys:
                if self.get(key) is None:
                    print(f"❌ 필수 설정 누락: {key}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ 설정 유효성 검증 실패: {e}")
            return False
    
    def print_config(self):
        """설정 출력"""
        import json
        print("📋 동기화 서비스 설정:")
        print("=" * 50)
        print(json.dumps(self.config, indent=2, ensure_ascii=False))

# 기본 설정 인스턴스
sync_config = SyncConfig()

# 환경 변수에서 설정 로드
def load_env_config():
    """환경 변수에서 설정 로드"""
    env_mapping = {
        "SYNC_DB_HOST": "database.host",
        "SYNC_DB_PORT": "database.port",
        "SYNC_DB_USER": "database.user",
        "SYNC_DB_PASSWORD": "database.password",
        "SYNC_DB_NAME": "database.database",
        "SYNC_API_BASE_URL": "api_server.base_url",
        "SYNC_LOG_LEVEL": "sync.log_level"
    }
    
    for env_var, config_path in env_mapping.items():
        env_value = os.getenv(env_var)
        if env_value:
            if config_path.endswith('.port'):
                try:
                    env_value = int(env_value)
                except ValueError:
                    continue
            
            sync_config.set(config_path, env_value)

# 환경 변수 설정 로드
load_env_config()
