from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.domain.user import (
    UserCreate, UserLogin, UserResponse, Token,
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.core.services.auth_service import (
    AuthService, AuthenticationError, UserAlreadyExistsError,
    InvalidTokenError
)
from app.adapters.inbound.auth_middleware import (
    get_auth_service, get_current_user, security
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    """Registra um novo usuário."""
    try:
        return await auth_service.register_user(user_data)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
) -> Token:
    """Autentica um usuário e retorna token de acesso."""
    try:
        return await auth_service.login_user(login_data)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """Retorna informações do usuário autenticado."""
    return current_user


@router.post("/forgot-password")
async def forgot_password(
    request_data: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """Solicita reset de senha."""
    await auth_service.request_password_reset(request_data)
    return {
        "message": "Se o e-mail existir, você receberá as instruções "
                   "para redefinir sua senha"
    }


@router.post("/reset-password")
async def reset_password(
    reset_data: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """Redefine a senha do usuário."""
    try:
        success = await auth_service.reset_password(reset_data)
        if success:
            return {"message": "Senha redefinida com sucesso"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno do servidor"
            )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.post("/refresh")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Token:
    """Renova o token de acesso."""
    # Valida token atual
    user = await auth_service.get_user_from_token(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Cria novo token
    # Como não temos a senha, vamos gerar um novo token diretamente
    from app.adapters.inbound.auth_middleware import _token_service
    access_token = _token_service.create_access_token(user.id)
    expires_in = _token_service.get_token_expiration_time()
    
    return Token(
        access_token=access_token,
        expires_in=expires_in,
        user=user
    )
