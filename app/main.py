"""
Ponto de entrada principal da aplicação FastAPI.

Este módulo configura e inicializa a aplicação FastAPI com todas as
configurações necessárias, middleware, rotas e documentação.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.inbound.auth_controller import router as auth_router
from app.adapters.inbound.health_controller import health_router
from app.config.settings import get_settings

# Configuração do logger
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gerencia o ciclo de vida da aplicação.

    Configura recursos na inicialização e limpa na finalização.
    """
    settings = get_settings()

    # Startup
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}")
    logger.info(f"Ambiente: {settings.environment}")
    logger.info(f"Debug: {settings.debug}")

    yield

    # Shutdown
    logger.info("Finalizando aplicação...")


def create_app() -> FastAPI:
    """
    Factory function para criar a aplicação FastAPI.

    Returns:
        FastAPI: Instância configurada da aplicação
    """
    settings = get_settings()

    # Configuração da aplicação
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
        # Configurações da documentação
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    # Configuração do CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
    )

    # Registro das rotas
    app.include_router(health_router)
    app.include_router(auth_router)

    # Importar e registrar router de contas
    from app.adapters.inbound.account_controller import (
        router as account_router,
    )

    app.include_router(account_router)

    # Importar e registrar routers de transações e categorias
    from app.adapters.inbound.category_controller import (
        router as category_router,
    )
    from app.adapters.inbound.transaction_controller import (
        router as transaction_router,
    )

    app.include_router(transaction_router)
    app.include_router(category_router)

    # Importar e registrar router de dashboard
    from app.adapters.controllers.dashboard_controller import (
        router as dashboard_router,
    )

    app.include_router(dashboard_router)

    # Importar e registrar routers de metas e orçamentos
    from app.adapters.inbound.budget_controller import router as budget_router
    from app.adapters.inbound.goal_controller import router as goal_router

    app.include_router(goal_router)
    app.include_router(budget_router)

    return app


# Instância da aplicação
app = create_app()
