"""Main FastAPI application with modular structure"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    dashboard_routes,
    ui_routes,
    match_routes,
    vssl_spec_routes
)

# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version
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
app.include_router(match_routes.router, prefix="/api/dashboard", tags=["Match"])
app.include_router(vssl_spec_routes.router, prefix="/api/dashboard", tags=["VsslSpec"])

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🚀 Port Dashboard API 시작됨")
    logger.info(f"📊 API 문서: http://{settings.host}:{settings.port}/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("🛑 Port Dashboard API 종료됨")

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=settings.host, 
        port=settings.port,
        log_level=settings.log_level.lower()
    )