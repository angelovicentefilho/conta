"""
Controller para health check da aplicação.

Fornece endpoints para verificação do status da aplicação e suas dependências.
"""

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter

from app.config import settings

# Router para os endpoints de health check
health_router = APIRouter(prefix="", tags=["Health Check"])


@health_router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Endpoint básico de health check.

    Retorna o status da aplicação e informações básicas.

    Returns:
        Dict contendo status da aplicação
    """
    return {
        "status": "OK",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "healthy",
    }


@health_router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Health check detalhado com informações das dependências.

    Returns:
        Dict contendo status detalhado da aplicação e dependências
    """
    return {
        "status": "OK",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {
            "mongodb": {
                "status": "not_checked",
                "url": settings.mongodb_url,
                "database": settings.mongodb_database,
            },
            "redis": {"status": "not_checked", "url": settings.redis_url},
        },
        "configuration": {
            "debug": settings.debug,
            "cors_origins": settings.cors_origins,
            "log_level": settings.log_level,
        },
    }
