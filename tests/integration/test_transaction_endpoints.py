"""
Testes de integração para endpoints de transações.

Valida o comportamento completo dos endpoints REST para gestão de transações.
"""

from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.domain.account import Account, AccountType
from app.core.domain.transaction import Category, TransactionType
from app.core.domain.user import User
from app.main import app


@pytest.fixture
def client():
    """Cliente de teste FastAPI."""
    return TestClient(app)


@pytest.fixture
def test_user():
    """Usuário de teste."""
    return User(
        id=uuid4(),
        name="Test User",
        email="test@example.com",
        password_hash="hashed_password",
    )


@pytest.fixture
def test_account(test_user):
    """Conta de teste."""
    return Account(
        id=uuid4(),
        user_id=test_user.id,
        name="Test Account",
        type=AccountType.CHECKING,
        balance=Decimal("1000.00"),
    )


@pytest.fixture
def test_category(test_user):
    """Categoria de teste."""
    return Category(
        id=uuid4(),
        user_id=test_user.id,
        name="Test Category",
        type=TransactionType.EXPENSE,
    )


@pytest.fixture
def auth_headers(client, test_user):
    """Headers de autenticação para testes."""
    # Primeiro registra o usuário
    register_data = {
        "name": test_user.name,
        "email": test_user.email,
        "password": "testpassword123",
    }

    response = client.post("/auth/register", json=register_data)
    assert response.status_code == 201

    # Depois faz login
    login_data = {"username": test_user.email, "password": "testpassword123"}

    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestTransactionEndpoints:
    """Testes para endpoints de transações."""

    def test_transaction_endpoints_are_registered(self, client):
        """Verifica se os endpoints de transação estão registrados."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        # Verifica se o OpenAPI schema contém endpoints de transação
        openapi_data = response.json()
        paths = openapi_data.get("paths", {})

        # Verifica se existe pelo menos um endpoint de transação
        transaction_paths = [
            path for path in paths.keys() if "transaction" in path
        ]
        assert len(transaction_paths) > 0, (
            f"Nenhum endpoint de transação encontrado. "
            f"Paths: {list(paths.keys())}"
        )

    def test_category_endpoints_are_registered(self, client):
        """Verifica se os endpoints de categoria estão registrados."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        # Verifica se o OpenAPI schema contém endpoints de categoria
        openapi_data = response.json()
        paths = openapi_data.get("paths", {})

        # Verifica se existe pelo menos um endpoint de categoria
        category_paths = [path for path in paths.keys() if "categor" in path]
        assert len(category_paths) > 0, (
            f"Nenhum endpoint de categoria encontrado. "
            f"Paths: {list(paths.keys())}"
        )


class TestCategoryEndpoints:
    """Testes para endpoints de categorias."""

    def test_category_creation_requires_auth(self, client):
        """Verifica que criação de categoria requer autenticação."""
        category_data = {"name": "Test Category", "type": "expense"}

        response = client.post("/api/v1/categories/", json=category_data)
        assert response.status_code == 403

    def test_list_categories_requires_auth(self, client):
        """Verifica que listagem de categorias requer autenticação."""
        response = client.get("/api/v1/categories/")
        assert response.status_code == 403
