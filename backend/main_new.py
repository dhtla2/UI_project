"""Main FastAPI application with modular structure"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# Import configuration and utilities
from config import settings
from utils import setup_logging, get_logger

# Import routers
from routers import (
    common_routes, 
    ais_routes, 
    tos_routes, 
    tc_routes, 
    qc_routes,
    yt_routes,
    dashboard_routes,
    ui_routes,
    match_routes,
    vssl_spec_routes
)

# Import Redis cache system
from services.cache.redis_manager import redis_manager
from config.redis_config import redis_settings

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 생명주기 관리
    
    Startup: Redis 캐시 서버 연결
    Shutdown: Redis 연결 해제
    """
    # ==================== Startup ====================
    logger.info("=" * 60)
    logger.info("🚀 Port Dashboard API 시작 중...")
    logger.info("=" * 60)
    
    # Redis 캐시 서버 연결
    if settings.redis_enabled:
        logger.info("🔴 Redis 캐시 서버 연결 중...")
        try:
            redis_connected = await redis_manager.connect(
                host=settings.redis_host,
                port=settings.redis_port,
                db=redis_settings.REDIS_DB,
                password=settings.redis_password,
                max_connections=redis_settings.REDIS_MAX_CONNECTIONS,
                socket_timeout=redis_settings.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=redis_settings.REDIS_SOCKET_CONNECT_TIMEOUT
            )
            
            if redis_connected:
                logger.info("✅ Redis 캐시 서버 연결 성공")
                redis_info = await redis_manager.get_info()
                logger.info(f"   - Redis 버전: {redis_info.get('version', 'N/A')}")
                logger.info(f"   - 사용 메모리: {redis_info.get('used_memory', 'N/A')}")
            else:
                logger.warning("⚠️ Redis 연결 실패 - 캐싱 비활성화 상태로 계속 실행")
                
        except Exception as e:
            logger.error(f"❌ Redis 연결 오류: {e}")
            logger.warning("⚠️ 캐싱 없이 서버 계속 실행")
    else:
        logger.info("ℹ️ Redis 캐싱이 비활성화되어 있습니다 (settings.redis_enabled=False)")
    
    logger.info("=" * 60)
    logger.info("✅ 서버 시작 완료!")
    logger.info(f"📍 API 문서: http://{settings.host}:{settings.port}/docs")
    logger.info("=" * 60)
    
    yield  # 서버 실행
    
    # ==================== Shutdown ====================
    logger.info("=" * 60)
    logger.info("🛑 Port Dashboard API 종료 중...")
    logger.info("=" * 60)
    
    # Redis 연결 해제
    if settings.redis_enabled:
        logger.info("🔴 Redis 연결 해제 중...")
        await redis_manager.disconnect()
        logger.info("✅ Redis 연결 해제 완료")
    
    logger.info("=" * 60)
    logger.info("✅ 서버 종료 완료")
    logger.info("=" * 60)


# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with proper prefixes
app.include_router(common_routes.router, tags=["Common"])
app.include_router(ui_routes.router, prefix="/ui", tags=["UI"])
app.include_router(dashboard_routes.router, prefix="/api/dashboard", tags=["Dashboard"])

# AIS routes - 기존 경로와 호환성 유지
app.include_router(ais_routes.router, prefix="/ais", tags=["AIS"])
# AIS dashboard routes - 기존 프론트엔드 호환
from routers.ais_routes import router as ais_dashboard_router
app.include_router(ais_dashboard_router, prefix="/api/dashboard", tags=["AIS Dashboard"], 
                  include_in_schema=False)  # 중복 스키마 방지

app.include_router(tos_routes.router, prefix="/api/dashboard", tags=["TOS"])
app.include_router(tc_routes.router, prefix="/api/dashboard", tags=["TC"])
app.include_router(qc_routes.router, prefix="/api/dashboard", tags=["QC"])
app.include_router(yt_routes.router, prefix="/api/dashboard", tags=["YT"])
app.include_router(match_routes.router, prefix="/api/dashboard", tags=["Match"])
app.include_router(vssl_spec_routes.router, prefix="/api/dashboard", tags=["VsslSpec"])

# Cache management routes (admin)
from routers import cache_routes
app.include_router(cache_routes.router, prefix="/api/admin/cache", tags=["Cache Management"])

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=settings.host, 
        port=settings.port,
        log_level=settings.log_level.lower()
    )