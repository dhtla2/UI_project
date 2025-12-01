"""캐싱 데코레이터 모듈"""

from functools import wraps
from typing import Callable, Optional, List
import json
import logging
from inspect import signature

from services.cache.redis_manager import redis_manager
from services.cache.cache_keys import CacheKeyGenerator
from config.redis_config import redis_settings

logger = logging.getLogger(__name__)


def cached(
    namespace: str,
    endpoint: str,
    ttl: Optional[int] = None,
    key_params: Optional[List[str]] = None,
    prefix: Optional[str] = None
):
    """
    캐싱 데코레이터
    
    함수 실행 전 Redis에서 캐시를 조회하고, 있으면 즉시 반환합니다.
    없으면 함수를 실행하고 결과를 Redis에 저장한 후 반환합니다.
    
    Args:
        namespace: 캐시 네임스페이스 (예: 'ais', 'tos', 'tc')
        endpoint: API 엔드포인트 식별자 (예: 'summary', 'quality')
        ttl: 캐시 유지 시간(초). None이면 CACHE_TTL_MEDIUM 사용
        key_params: 캐시 키에 포함할 함수 파라미터 이름 리스트
        prefix: 캐시 프리픽스. None이면 설정값 사용
    
    Examples:
        >>> @cached(namespace='ais', endpoint='summary', ttl=3600)
        >>> async def get_ais_summary():
        >>>     # DB 쿼리...
        >>>     return data
        
        >>> @cached(
        >>>     namespace='ais',
        >>>     endpoint='history',
        >>>     ttl=1800,
        >>>     key_params=['period', 'start_date', 'end_date']
        >>> )
        >>> async def get_ais_history(period, start_date, end_date):
        >>>     # DB 쿼리...
        >>>     return data
    """
    
    # 기본값 설정
    if ttl is None:
        ttl = redis_settings.CACHE_TTL_MEDIUM
    
    if prefix is None:
        prefix = redis_settings.CACHE_PREFIX
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 디버그: 데코레이터 진입 확인
            logger.info(f"🔍 [캐시 데코레이터] 진입: {func.__name__} (namespace={namespace}, endpoint={endpoint})")
            
            # ==================== Redis 클라이언트 확인 ====================
            try:
                redis_client = redis_manager.get_client()
            except RuntimeError as e:
                # Redis 미연결 시 원본 함수 실행 (Graceful Degradation)
                logger.warning(
                    f"⚠️ Redis 미연결, 캐시 없이 실행: {func.__name__} - {e}"
                )
                return await func(*args, **kwargs)
            
            # ==================== 캐시 키 생성 ====================
            cache_params = {}
            
            if key_params:
                # 함수 시그니처에서 파라미터 추출
                sig = signature(func)
                try:
                    bound_args = sig.bind(*args, **kwargs)
                    bound_args.apply_defaults()
                    
                    for param_name in key_params:
                        if param_name in bound_args.arguments:
                            value = bound_args.arguments[param_name]
                            # None이 아닌 값만 포함
                            if value is not None:
                                cache_params[param_name] = value
                                
                except Exception as e:
                    logger.error(f"파라미터 바인딩 오류: {e}")
            
            cache_key = CacheKeyGenerator.generate(
                namespace=namespace,
                endpoint=endpoint,
                params=cache_params if cache_params else None,
                prefix=prefix
            )
            
            # ==================== 캐시 조회 ====================
            try:
                cached_data = await redis_client.get(cache_key)
                
                if cached_data:
                    logger.info(f"✅ 캐시 HIT: {cache_key}")
                    
                    # JSON 파싱하여 반환
                    try:
                        return json.loads(cached_data)
                    except json.JSONDecodeError as e:
                        logger.error(f"캐시 데이터 파싱 오류: {e}")
                        # 파싱 실패 시 캐시 삭제하고 원본 함수 실행
                        await redis_client.delete(cache_key)
                
                logger.info(f"❌ 캐시 MISS: {cache_key}")
                
            except Exception as e:
                logger.error(f"캐시 조회 오류: {e}")
                # 에러 발생 시 원본 함수 실행
            
            # ==================== 원본 함수 실행 ====================
            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"함수 실행 오류 ({func.__name__}): {e}")
                raise
            
            # ==================== 캐시 저장 ====================
            try:
                # JSON 직렬화
                serialized_data = json.dumps(
                    result,
                    ensure_ascii=False,
                    default=str  # datetime 등 특수 타입 처리
                )
                
                # Redis에 저장
                await redis_client.setex(
                    name=cache_key,
                    time=ttl,
                    value=serialized_data
                )
                
                logger.info(f"💾 캐시 저장: {cache_key} (TTL: {ttl}s)")
                
            except Exception as e:
                logger.error(f"캐시 저장 오류: {e}")
                # 저장 실패해도 결과는 반환 (Graceful Degradation)
            
            return result
        
        # 데코레이터 메타데이터 저장 (디버깅/모니터링용)
        wrapper._cache_config = {
            'namespace': namespace,
            'endpoint': endpoint,
            'ttl': ttl,
            'key_params': key_params,
            'prefix': prefix
        }
        
        return wrapper
    
    return decorator


def cache_response(ttl: int = None):
    """
    간단한 캐싱 데코레이터 (FastAPI Response 전용)
    
    경로와 쿼리 파라미터를 자동으로 캐시 키로 사용합니다.
    
    Args:
        ttl: 캐시 유지 시간(초)
    
    Examples:
        >>> @app.get("/api/data")
        >>> @cache_response(ttl=300)
        >>> async def get_data(param1: str, param2: int):
        >>>     return {"data": "value"}
    """
    if ttl is None:
        ttl = redis_settings.CACHE_TTL_MEDIUM
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 함수명을 namespace로 사용
            namespace = "api"
            endpoint = func.__name__
            
            # 모든 kwargs를 key_params로 사용
            cache_params = {k: v for k, v in kwargs.items() if v is not None}
            
            # 캐시 키 생성
            cache_key = CacheKeyGenerator.generate(
                namespace=namespace,
                endpoint=endpoint,
                params=cache_params if cache_params else None
            )
            
            try:
                redis_client = redis_manager.get_client()
                
                # 캐시 조회
                cached_data = await redis_client.get(cache_key)
                if cached_data:
                    logger.info(f"✅ 캐시 HIT: {cache_key}")
                    return json.loads(cached_data)
                
                logger.info(f"❌ 캐시 MISS: {cache_key}")
                
                # 원본 함수 실행
                result = await func(*args, **kwargs)
                
                # 캐시 저장
                await redis_client.setex(
                    name=cache_key,
                    time=ttl,
                    value=json.dumps(result, ensure_ascii=False, default=str)
                )
                logger.info(f"💾 캐시 저장: {cache_key}")
                
                return result
                
            except RuntimeError:
                # Redis 미연결 시 원본 함수만 실행
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"캐시 처리 오류: {e}")
                return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


# ==================== 캐시 통계 추적 (선택적) ====================
class CacheStats:
    """캐시 히트/미스 통계 추적"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.errors = 0
    
    def record_hit(self):
        """캐시 히트 기록"""
        self.hits += 1
    
    def record_miss(self):
        """캐시 미스 기록"""
        self.misses += 1
    
    def record_error(self):
        """캐시 에러 기록"""
        self.errors += 1
    
    def get_hit_rate(self) -> float:
        """캐시 히트율 계산"""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100
    
    def get_stats(self) -> dict:
        """통계 반환"""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "errors": self.errors,
            "hit_rate": f"{self.get_hit_rate():.2f}%",
            "total_requests": self.hits + self.misses
        }
    
    def reset(self):
        """통계 초기화"""
        self.hits = 0
        self.misses = 0
        self.errors = 0


# 전역 캐시 통계 인스턴스
cache_stats = CacheStats()

