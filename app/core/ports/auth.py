from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime

from app.core.domain.user import (
    User, UserCreate, PasswordResetToken
)


class UserRepositoryPort(ABC):
    """Interface para repositório de usuários."""

    @abstractmethod
    async def create_user(self, user_data: UserCreate) -> User:
        """Cria um novo usuário."""
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Busca usuário por ID."""
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por e-mail."""
        pass

    @abstractmethod
    async def update_user_password(
        self, user_id: str, password_hash: str
    ) -> bool:
        """Atualiza a senha do usuário."""
        pass

    @abstractmethod
    async def deactivate_user(self, user_id: str) -> bool:
        """Desativa um usuário."""
        pass


class PasswordResetRepositoryPort(ABC):
    """Interface para repositório de tokens de reset de senha."""

    @abstractmethod
    async def create_reset_token(
        self, user_id: str, token_hash: str, expires_at: datetime
    ) -> PasswordResetToken:
        """Cria um token de reset de senha."""
        pass

    @abstractmethod
    async def get_valid_reset_token(
        self, token_hash: str
    ) -> Optional[PasswordResetToken]:
        """Busca token válido de reset (não usado e não expirado)."""
        pass

    @abstractmethod
    async def mark_token_as_used(self, token_id: str) -> bool:
        """Marca um token como usado."""
        pass

    @abstractmethod
    async def cleanup_expired_tokens(self) -> int:
        """Remove tokens expirados. Retorna quantidade removida."""
        pass


class TokenServicePort(ABC):
    """Interface para serviço de tokens JWT."""

    @abstractmethod
    def create_access_token(self, user_id: str) -> str:
        """Cria um token de acesso JWT."""
        pass

    @abstractmethod
    def verify_token(self, token: str) -> Optional[str]:
        """Verifica e decodifica token JWT. Retorna user_id se válido."""
        pass

    @abstractmethod
    def get_token_expiration_time(self) -> int:
        """Retorna o tempo de expiração do token em segundos."""
        pass


class PasswordServicePort(ABC):
    """Interface para serviço de hashing de senhas."""

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Gera hash da senha."""
        pass

    @abstractmethod
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verifica se a senha corresponde ao hash."""
        pass


class EmailServicePort(ABC):
    """Interface para serviço de e-mail."""

    @abstractmethod
    async def send_password_reset_email(
        self, email: str, reset_token: str, user_name: str
    ) -> bool:
        """Envia e-mail de reset de senha."""
        pass
