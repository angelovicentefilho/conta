import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class UserBase(BaseModel):
    """Modelo base para User com campos comuns."""

    name: str
    email: EmailStr


class UserCreate(UserBase):
    """Modelo para criação de usuário."""

    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Valida se a senha atende aos critérios de segurança."""
        if len(v) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")

        if not re.search(r"[A-Z]", v):
            raise ValueError(
                "Senha deve conter pelo menos uma letra maiúscula"
            )

        if not re.search(r"[a-z]", v):
            raise ValueError(
                "Senha deve conter pelo menos uma letra minúscula"
            )

        if not re.search(r"\d", v):
            raise ValueError("Senha deve conter pelo menos um número")

        if not re.search(r"[@#$%&*!?]", v):
            raise ValueError(
                "Senha deve conter pelo menos um caractere "
                "especial (@#$%&*!?)"
            )

        return v


class UserLogin(BaseModel):
    """Modelo para login de usuário."""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Modelo de resposta do usuário (sem senha)."""

    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class User(UserBase):
    """Modelo completo do usuário para persistência."""

    id: str
    password_hash: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Modelo de resposta do token."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Dados extraídos do token."""

    user_id: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    """Modelo para solicitação de reset de senha."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Modelo para reset de senha."""

    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Valida se a nova senha atende aos critérios de segurança."""
        if len(v) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")

        if not re.search(r"[A-Z]", v):
            raise ValueError(
                "Senha deve conter pelo menos uma letra maiúscula"
            )

        if not re.search(r"[a-z]", v):
            raise ValueError(
                "Senha deve conter pelo menos uma letra minúscula"
            )

        if not re.search(r"\d", v):
            raise ValueError("Senha deve conter pelo menos um número")

        if not re.search(r"[@#$%&*!?]", v):
            raise ValueError(
                "Senha deve conter pelo menos um caractere "
                "especial (@#$%&*!?)"
            )

        return v


class PasswordResetToken(BaseModel):
    """Modelo para token de reset de senha."""

    id: str
    user_id: str
    token_hash: str
    expires_at: datetime
    used: bool = False
    created_at: datetime
