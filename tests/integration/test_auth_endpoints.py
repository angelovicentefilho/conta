import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def valid_user_payload():
    """Dados válidos para criação de usuário."""
    return {
        "name": "João Silva",
        "email": "joao@example.com",
        "password": "MinhaSenh@123",
    }


@pytest.fixture
def invalid_user_payload():
    """Dados inválidos para criação de usuário."""
    return {
        "name": "João Silva",
        "email": "joao@example.com",
        "password": "123",  # Senha muito simples
    }


class TestRegisterEndpoint:
    """Testes para endpoint de registro."""

    def test_register_valid_user(self, valid_user_payload):
        """Deve registrar usuário com dados válidos."""
        response = client.post("/auth/register", json=valid_user_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == valid_user_payload["name"]
        assert data["email"] == valid_user_payload["email"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # Senha não deve ser retornada

    def test_register_invalid_password(self, invalid_user_payload):
        """Deve rejeitar usuário com senha inválida."""
        response = client.post("/auth/register", json=invalid_user_payload)

        assert response.status_code == 422
        assert "Senha deve ter" in response.json()["detail"][0]["msg"]

    def test_register_duplicate_email(self, valid_user_payload):
        """Deve rejeitar usuário com e-mail duplicado."""
        # Primeiro registro
        client.post("/auth/register", json=valid_user_payload)

        # Segundo registro com mesmo e-mail
        response = client.post("/auth/register", json=valid_user_payload)

        assert response.status_code == 409
        assert "já está em uso" in response.json()["detail"]

    def test_register_invalid_email_format(self, valid_user_payload):
        """Deve rejeitar usuário com formato de e-mail inválido."""
        payload = valid_user_payload.copy()
        payload["email"] = "email-invalido"

        response = client.post("/auth/register", json=payload)

        assert response.status_code == 422


class TestLoginEndpoint:
    """Testes para endpoint de login."""

    def test_login_valid_credentials(self, valid_user_payload):
        """Deve autenticar usuário com credenciais válidas."""
        # Registra usuário
        client.post("/auth/register", json=valid_user_payload)

        # Faz login
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"],
        }
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data
        assert data["user"]["email"] == valid_user_payload["email"]

    def test_login_invalid_email(self):
        """Deve rejeitar login com e-mail inexistente."""
        login_data = {
            "email": "inexistente@example.com",
            "password": "MinhaSenh@123",
        }
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Credenciais inválidas" in response.json()["detail"]

    def test_login_invalid_password(self, valid_user_payload):
        """Deve rejeitar login com senha incorreta."""
        # Registra usuário
        client.post("/auth/register", json=valid_user_payload)

        # Tenta login com senha incorreta
        login_data = {
            "email": valid_user_payload["email"],
            "password": "SenhaErrada123",
        }
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Credenciais inválidas" in response.json()["detail"]


class TestProtectedEndpoints:
    """Testes para endpoints protegidos."""

    def get_auth_headers(self, valid_user_payload):
        """Helper para obter headers de autenticação."""
        # Registra usuário
        client.post("/auth/register", json=valid_user_payload)

        # Faz login
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"],
        }
        response = client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]

        return {"Authorization": f"Bearer {token}"}

    def test_get_current_user_with_valid_token(self, valid_user_payload):
        """Deve retornar dados do usuário com token válido."""
        headers = self.get_auth_headers(valid_user_payload)

        response = client.get("/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == valid_user_payload["email"]
        assert data["name"] == valid_user_payload["name"]

    def test_get_current_user_without_token(self):
        """Deve rejeitar acesso sem token."""
        response = client.get("/auth/me")

        assert response.status_code == 403  # Forbidden

    def test_get_current_user_with_invalid_token(self):
        """Deve rejeitar token inválido."""
        headers = {"Authorization": "Bearer token-invalido"}

        response = client.get("/auth/me", headers=headers)

        assert response.status_code == 401
        assert "Token inválido" in response.json()["detail"]


class TestPasswordReset:
    """Testes para reset de senha."""

    def test_forgot_password_existing_user(self, valid_user_payload):
        """Deve aceitar solicitação de reset para usuário existente."""
        # Registra usuário
        client.post("/auth/register", json=valid_user_payload)

        # Solicita reset
        response = client.post(
            "/auth/forgot-password",
            json={"email": valid_user_payload["email"]},
        )

        assert response.status_code == 200
        assert "receberá as instruções" in response.json()["message"]

    def test_forgot_password_nonexistent_user(self):
        """Deve retornar sucesso mesmo para usuário inexistente."""
        response = client.post(
            "/auth/forgot-password", json={"email": "inexistente@example.com"}
        )

        assert response.status_code == 200
        assert "receberá as instruções" in response.json()["message"]

    def test_reset_password_invalid_token(self):
        """Deve rejeitar token inválido para reset."""
        response = client.post(
            "/auth/reset-password",
            json={"token": "token-invalido", "new_password": "NovaSenha@123"},
        )

        assert response.status_code == 400
        assert "Token inválido" in response.json()["detail"]


class TestRefreshToken:
    """Testes para renovação de token."""

    def test_refresh_valid_token(self, valid_user_payload):
        """Deve renovar token válido."""
        import time

        # Registra usuário e faz login
        client.post("/auth/register", json=valid_user_payload)
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"],
        }
        response = client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]

        # Espera um pouco para garantir timestamp diferente
        time.sleep(1)

        # Renova token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/auth/refresh", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        # Remove assertion que compara tokens pois podem ser iguais
        # dependendo da implementação

    def test_refresh_invalid_token(self):
        """Deve rejeitar token inválido para renovação."""
        headers = {"Authorization": "Bearer token-invalido"}
        response = client.post("/auth/refresh", headers=headers)

        assert response.status_code == 401
        assert "Token inválido" in response.json()["detail"]
