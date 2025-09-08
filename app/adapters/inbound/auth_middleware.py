from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.adapters.outbound.email_service import MockEmailService
from app.adapters.outbound.jwt_service import JWTTokenService
from app.adapters.outbound.memory_repositories import (
    InMemoryPasswordResetRepository,
    InMemoryUserRepository,
)
from app.adapters.outbound.password_service import BcryptPasswordService
from app.core.domain.user import UserResponse
from app.core.services.auth_service import AuthService

# Security scheme
security = HTTPBearer()

# Dependências de serviços (instâncias globais para desenvolvimento)
_user_repository = InMemoryUserRepository()
_password_reset_repository = InMemoryPasswordResetRepository()
_token_service = JWTTokenService()
_password_service = BcryptPasswordService()
_email_service = MockEmailService()

_auth_service = AuthService(
    user_repository=_user_repository,
    password_reset_repository=_password_reset_repository,
    token_service=_token_service,
    password_service=_password_service,
    email_service=_email_service,
)


def get_auth_service() -> AuthService:
    """Retorna instância do serviço de autenticação."""
    return _auth_service


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Middleware para extrair usuário autenticado do token."""
    token = credentials.credentials

    user = await auth_service.get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[UserResponse]:
    """Middleware opcional para extrair usuário (não obrigatório)."""
    if not credentials:
        return None

    token = credentials.credentials
    return await auth_service.get_user_from_token(token)
