"""
Configuração de testes para pytest.

Este módulo contém fixtures e configurações compartilhadas
entre todos os testes da aplicação.
"""

import pytest
from fastapi.testclient import TestClient

from app.adapters.inbound.account_controller import _account_repository
from app.adapters.inbound.auth_middleware import (
    _password_reset_repository,
    _user_repository,
)
from app.adapters.inbound.transaction_controller import (
    _category_repository,
    _transaction_repository,
)
from app.main import app


@pytest.fixture(autouse=True)
def clear_repositories():
    """
    Fixture que limpa todos os repositórios antes de cada teste.
    """
    _user_repository.clear()
    _password_reset_repository.clear()
    _account_repository.clear()
    _transaction_repository.clear()
    _category_repository.clear()
    yield


@pytest.fixture
def client():
    """
    Fixture que fornece um cliente de teste para a aplicação FastAPI.

    Returns:
        TestClient: Cliente configurado para testes
    """
    return TestClient(app)


@pytest.fixture
def sample_user_data():
    """
    Fixture com dados de usuário para testes.

    Returns:
        dict: Dados de usuário de exemplo
    """
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "name": "Test User",
    }


@pytest.fixture
def sample_account_data():
    """
    Fixture com dados de conta financeira para testes.

    Returns:
        dict: Dados de conta de exemplo
    """
    return {
        "name": "Conta Corrente Principal",
        "type": "checking",
        "initial_balance": 1000.00,
        "currency": "BRL",
        "is_primary": True,
    }


@pytest.fixture
def sample_transaction_data():
    """
    Fixture com dados de transação para testes.

    Returns:
        dict: Dados de transação de exemplo
    """
    return {
        "description": "Compra no supermercado",
        "amount": -150.75,
        "type": "expense",
        "category": "food",
        "date": "2024-01-15",
    }
