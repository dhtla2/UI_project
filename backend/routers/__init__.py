"""Routers package initialization"""

from . import (
    common_routes,
    ais_routes,
    tos_routes,
    tc_routes,
    qc_routes,
    yt_routes,
    dashboard_routes,
    ui_routes,
    match_routes,
    vssl_spec_routes,
    cache_routes
)

__all__ = [
    "common_routes",
    "ais_routes", 
    "tos_routes",
    "tc_routes",
    "qc_routes",
    "yt_routes",
    "dashboard_routes",
    "ui_routes",
    "match_routes",
    "vssl_spec_routes",
    "cache_routes"
]