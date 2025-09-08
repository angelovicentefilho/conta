from datetime import datetime

import pytest

from app.adapters.outbound.email_service import MockEmailService
from app.adapters.outbound.jwt_service import JWTTokenService
from app.adapters.outbound.memory_repositories import (
    InMemoryPasswordResetRepository,
    InMemoryUserRepository,
)
from app.adapters.outbound.password_service import BcryptPasswordService
from app.core.domain.user import UserCreate, UserLogin
from app.core.services.auth_service import (
    AuthenticationError,
    AuthService,
    UserAlreadyExistsError,
)


@pytest.fixture
def auth_service():
    """Fixture para criar instância do serviço de autenticação."""
    user_repo = InMemoryUserRepository()
    password_reset_repo = InMemoryPasswordResetRepository()
    token_service = JWTTokenService()
    password_service = BcryptPasswordService()
    email_service = MockEmailService()

    return AuthService(
        user_repository=user_repo,
        password_reset_repository=password_reset_repo,
        token_service=token_service,
        password_service=password_service,
        email_service=email_service,
    )


@pytest.fixture
def valid_user_data():
    """Fixture com dados válidos de usuário."""
    return UserCreate(
        name="João Silva", email="joao@example.com", password="MinhaSenh@123"
    )


class TestUserRegistration:
    """Testes para registro de usuário."""

    async def test_register_valid_user(self, auth_service, valid_user_data):
        """Deve registrar usuário com dados válidos."""
        user = await auth_service.register_user(valid_user_data)

        assert user.name == valid_user_data.name
        assert user.email == valid_user_data.email
        assert user.id is not None
        assert isinstance(user.created_at, datetime)

    async def test_register_duplicate_email(
        self, auth_service, valid_user_data
    ):
        """Deve rejeitar usuário com e-mail duplicado."""
        # Registra primeiro usuário
        await auth_service.register_user(valid_user_data)

        # Tenta registrar novamente
        with pytest.raises(UserAlreadyExistsError):
            await auth_service.register_user(valid_user_data)

    def test_invalid_password_validation(self):
        """Deve validar formato da senha na criação do modelo."""
        with pytest.raises(ValueError, match="Senha deve ter"):
            UserCreate(
                name="João Silva",
                email="joao@example.com",
                password="123",  # Senha muito simples
            )


class TestUserLogin:
    """Testes para login de usuário."""

    async def test_login_valid_credentials(
        self, auth_service, valid_user_data
    ):
        """Deve autenticar usuário com credenciais válidas."""
        # Registra usuário
        registered_user = await auth_service.register_user(valid_user_data)

        # Faz login
        login_data = UserLogin(
            email=valid_user_data.email, password=valid_user_data.password
        )
        token = await auth_service.login_user(login_data)

        assert token.access_token is not None
        assert token.token_type == "bearer"
        assert token.expires_in > 0
        assert token.user.id == registered_user.id

    async def test_login_invalid_email(self, auth_service):
        """Deve rejeitar login com e-mail inexistente."""
        login_data = UserLogin(
            email="inexistente@example.com", password="MinhaSenh@123"
        )

        with pytest.raises(AuthenticationError):
            await auth_service.login_user(login_data)

    async def test_login_invalid_password(self, auth_service, valid_user_data):
        """Deve rejeitar login com senha incorreta."""
        # Registra usuário
        await auth_service.register_user(valid_user_data)

        # Tenta login com senha incorreta
        login_data = UserLogin(
            email=valid_user_data.email, password="SenhaErrada123"
        )

        with pytest.raises(AuthenticationError):
            await auth_service.login_user(login_data)


class TestTokenValidation:
    """Testes para validação de tokens."""

    async def test_valid_token_extraction(self, auth_service, valid_user_data):
        """Deve extrair usuário de token válido."""
        # Registra e faz login
        registered_user = await auth_service.register_user(valid_user_data)
        login_data = UserLogin(
            email=valid_user_data.email, password=valid_user_data.password
        )
        token = await auth_service.login_user(login_data)

        # Valida token
        user = await auth_service.get_user_from_token(token.access_token)

        assert user is not None
        assert user.id == registered_user.id
        assert user.email == registered_user.email

    async def test_invalid_token(self, auth_service):
        """Deve rejeitar token inválido."""
        user = await auth_service.get_user_from_token("token-invalido")
        assert user is None

    async def test_empty_token(self, auth_service):
        """Deve rejeitar token vazio."""
        user = await auth_service.get_user_from_token("")
        assert user is None


class TestPasswordServices:
    """Testes para serviços de senha."""

    def test_password_hashing(self):
        """Deve criar hash da senha corretamente."""
        password_service = BcryptPasswordService()
        password = "MinhaSenh@123"

        hashed = password_service.hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert password_service.verify_password(password, hashed)

    def test_password_verification_invalid(self):
        """Deve rejeitar senha incorreta."""
        password_service = BcryptPasswordService()
        password = "MinhaSenh@123"
        wrong_password = "SenhaErrada"

        hashed = password_service.hash_password(password)

        assert not password_service.verify_password(wrong_password, hashed)


class TestJWTTokenService:
    """Testes para serviço de tokens JWT."""

    def test_token_creation_and_verification(self):
        """Deve criar e verificar token corretamente."""
        token_service = JWTTokenService()
        user_id = "user-123"

        token = token_service.create_access_token(user_id)
        verified_user_id = token_service.verify_token(token)

        assert token is not None
        assert verified_user_id == user_id

    def test_invalid_token_verification(self):
        """Deve rejeitar token inválido."""
        token_service = JWTTokenService()

        result = token_service.verify_token("token-invalido")
        assert result is None

    def test_token_expiration_time(self):
        """Deve retornar tempo de expiração correto."""
        token_service = JWTTokenService()
        expiration = token_service.get_token_expiration_time()

        assert expiration > 0
        assert isinstance(expiration, int)
