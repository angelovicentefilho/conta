from datetime import datetime, timedelta
from typing import Optional
import secrets

from app.core.domain.user import (
    UserCreate, UserLogin, UserResponse, Token,
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.core.ports.auth import (
    UserRepositoryPort, PasswordResetRepositoryPort,
    TokenServicePort, PasswordServicePort, EmailServicePort
)


class AuthenticationError(Exception):
    """Erro de autenticação."""
    pass


class UserAlreadyExistsError(Exception):
    """Usuário já existe."""
    pass


class InvalidTokenError(Exception):
    """Token inválido."""
    pass


class AuthService:
    """Serviço de autenticação."""

    def __init__(
        self,
        user_repository: UserRepositoryPort,
        password_reset_repository: PasswordResetRepositoryPort,
        token_service: TokenServicePort,
        password_service: PasswordServicePort,
        email_service: EmailServicePort,
    ):
        self._user_repository = user_repository
        self._password_reset_repository = password_reset_repository
        self._token_service = token_service
        self._password_service = password_service
        self._email_service = email_service

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """Registra um novo usuário."""
        # Verifica se usuário já existe
        existing_user = await self._user_repository.get_user_by_email(
            user_data.email
        )
        if existing_user:
            raise UserAlreadyExistsError("E-mail já está em uso")

        # Cria hash da senha
        password_hash = self._password_service.hash_password(
            user_data.password
        )

        # Cria usuário com dados completos
        user_to_create = UserCreate(
            name=user_data.name,
            email=user_data.email,
            password=password_hash  # Aqui já é o hash
        )

        # Salva no repositório
        created_user = await self._user_repository.create_user(
            user_to_create
        )

        return UserResponse(
            id=created_user.id,
            name=created_user.name,
            email=created_user.email,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at
        )

    async def login_user(self, login_data: UserLogin) -> Token:
        """Autentica um usuário e retorna token."""
        # Busca usuário
        user = await self._user_repository.get_user_by_email(
            login_data.email
        )
        if not user or not user.is_active:
            raise AuthenticationError("Credenciais inválidas")

        # Verifica senha
        if not self._password_service.verify_password(
            login_data.password, user.password_hash
        ):
            raise AuthenticationError("Credenciais inválidas")

        # Gera token
        access_token = self._token_service.create_access_token(user.id)
        expires_in = self._token_service.get_token_expiration_time()

        user_response = UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

        return Token(
            access_token=access_token,
            expires_in=expires_in,
            user=user_response
        )

    async def get_user_from_token(self, token: str) -> Optional[UserResponse]:
        """Extrai usuário válido do token."""
        user_id = self._token_service.verify_token(token)
        if not user_id:
            return None

        user = await self._user_repository.get_user_by_id(user_id)
        if not user or not user.is_active:
            return None

        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    async def request_password_reset(
        self, request_data: ForgotPasswordRequest
    ) -> bool:
        """Solicita reset de senha."""
        user = await self._user_repository.get_user_by_email(
            request_data.email
        )
        if not user or not user.is_active:
            # Por segurança, sempre retorna True mesmo se usuário não existir
            return True

        # Gera token único
        reset_token = secrets.token_urlsafe(32)
        token_hash = self._password_service.hash_password(reset_token)

        # Define expiração (1 hora)
        expires_at = datetime.utcnow() + timedelta(hours=1)

        # Salva token no banco
        await self._password_reset_repository.create_reset_token(
            user.id, token_hash, expires_at
        )

        # Envia e-mail
        await self._email_service.send_password_reset_email(
            user.email, reset_token, user.name
        )

        return True

    async def reset_password(
        self, reset_data: ResetPasswordRequest
    ) -> bool:
        """Reseta a senha do usuário."""
        # Verifica token
        token_hash = self._password_service.hash_password(reset_data.token)
        reset_token = await self._password_reset_repository.get_valid_reset_token(  # noqa: E501
            token_hash
        )

        if not reset_token:
            raise InvalidTokenError("Token inválido ou expirado")

        # Atualiza senha
        new_password_hash = self._password_service.hash_password(
            reset_data.new_password
        )

        success = await self._user_repository.update_user_password(
            reset_token.user_id, new_password_hash
        )

        if success:
            # Marca token como usado
            await self._password_reset_repository.mark_token_as_used(
                reset_token.id
            )

        return success

    async def cleanup_expired_tokens(self) -> int:
        """Remove tokens expirados."""
        return await self._password_reset_repository.cleanup_expired_tokens()
