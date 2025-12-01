"""Redis 설정 모듈"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class RedisSettings(BaseSettings):
    """Redis 연결 및 캐시 설정"""
    
    # ==================== Redis 서버 정보 ====================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = "PortDashboard2024!"
    
    # ==================== 커넥션 풀 설정 ====================
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5
    REDIS_SOCKET_KEEPALIVE: bool = True
    
    # ==================== 캐시 TTL (Time To Live) 설정 ====================
    # 실시간성이 중요한 데이터
    CACHE_TTL_SHORT: int = 300          # 5분 (300초)
    
    # 보통 변경되는 데이터
    CACHE_TTL_MEDIUM: int = 1800        # 30분 (1,800초)
    
    # 거의 변경되지 않는 데이터
    CACHE_TTL_LONG: int = 3600          # 1시간 (3,600초)
    
    # 통계 데이터 (일 단위 변경)
    CACHE_TTL_VERY_LONG: int = 86400    # 24시간 (86,400초)
    
    # ==================== 캐시 네임스페이스 ====================
    CACHE_PREFIX: str = "port_dashboard"
    
    # ==================== 설정 로드 ====================
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
    
    # ==================== 연결 URL 생성 ====================
    def get_redis_url(self) -> str:
        """Redis 연결 URL 반환"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


# 싱글톤 인스턴스
redis_settings = RedisSettings()


# ==================== TTL 헬퍼 함수 ====================
def get_ttl_for_endpoint(endpoint_type: str) -> int:
    """
    엔드포인트 타입에 따라 적절한 TTL 반환
    
    Args:
        endpoint_type: 'summary', 'detail', 'history', 'realtime'
    
    Returns:
        TTL (초)
    """
    ttl_mapping = {
        'summary': redis_settings.CACHE_TTL_LONG,        # 요약 데이터: 1시간
        'detail': redis_settings.CACHE_TTL_MEDIUM,       # 상세 데이터: 30분
        'history': redis_settings.CACHE_TTL_MEDIUM,      # 히스토리: 30분
        'realtime': redis_settings.CACHE_TTL_SHORT,      # 실시간: 5분
        'statistics': redis_settings.CACHE_TTL_VERY_LONG # 통계: 24시간
    }
    
    return ttl_mapping.get(endpoint_type, redis_settings.CACHE_TTL_MEDIUM)


if __name__ == "__main__":
    # 설정 테스트
    print("=" * 60)
    print("Redis 설정 확인")
    print("=" * 60)
    print(f"Redis Host: {redis_settings.REDIS_HOST}")
    print(f"Redis Port: {redis_settings.REDIS_PORT}")
    print(f"Redis DB: {redis_settings.REDIS_DB}")
    print(f"Redis Password: {'설정됨' if redis_settings.REDIS_PASSWORD else '미설정'}")
    print(f"Connection Pool Size: {redis_settings.REDIS_MAX_CONNECTIONS}")
    print(f"Cache Prefix: {redis_settings.CACHE_PREFIX}")
    print(f"\nTTL 설정:")
    print(f"  - SHORT (5분): {redis_settings.CACHE_TTL_SHORT}초")
    print(f"  - MEDIUM (30분): {redis_settings.CACHE_TTL_MEDIUM}초")
    print(f"  - LONG (1시간): {redis_settings.CACHE_TTL_LONG}초")
    print(f"  - VERY_LONG (24시간): {redis_settings.CACHE_TTL_VERY_LONG}초")
    print(f"\nRedis URL: {redis_settings.get_redis_url()}")

