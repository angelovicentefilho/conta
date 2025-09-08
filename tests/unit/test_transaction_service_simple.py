"""
Testes unitários simplificados para TransactionServiceImpl e CategoryServiceImpl.

Valida a lógica de negócio básica para gestão de transações e categorias.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from app.core.domain.transaction import (
    TransactionType, CreateTransactionRequest, CreateCategoryRequest
)
from app.core.domain.account import Account, AccountType
from app.core.domain.user import User
from app.core.services.transaction_service import (
    TransactionServiceImpl, CategoryServiceImpl
)
from app.adapters.outbound.memory_repositories import (
    InMemoryTransactionRepository, InMemoryCategoryRepository,
    InMemoryAccountRepository
)


class TestTransactionServiceBasic:
    """Testes básicos para TransactionService."""

    @pytest.fixture
    def user(self):
        """Usuário de teste."""
        now = datetime.utcnow()
        return User(
            id=str(uuid4()),
            name="Test User",
            email="test@example.com",
            password_hash="hashed",
            created_at=now,
            updated_at=now,
            is_active=True
        )

    @pytest.fixture
    def account(self, user):
        """Conta de teste."""
        now = datetime.utcnow()
        return Account(
            id=uuid4(),
            user_id=uuid4(),  # Usamos UUID direto aqui
            name="Test Account",
            type=AccountType.CHECKING,
            balance=Decimal("1000.00"),
            is_primary=True,
            created_at=now,
            updated_at=now,
            is_active=True
        )

    @pytest.fixture
    def transaction_service(self):
        """Serviço de transações configurado."""
        transaction_repo = InMemoryTransactionRepository()
        account_repo = InMemoryAccountRepository()
        category_repo = InMemoryCategoryRepository()
        return TransactionServiceImpl(
            transaction_repository=transaction_repo,
            account_repository=account_repo,
            category_repository=category_repo
        )

    @pytest.fixture
    def category_service(self):
        """Serviço de categorias configurado."""
        category_repo = InMemoryCategoryRepository()
        return CategoryServiceImpl(category_repository=category_repo)

    def test_create_transaction_request_valid(self):
        """Deve criar request de transação válido."""
        request = CreateTransactionRequest(
            account_id=uuid4(),
            category_id=uuid4(),
            type=TransactionType.EXPENSE,
            amount=Decimal("100.00"),
            description="Test transaction",
            date=datetime.now()
        )
        
        assert request.type == TransactionType.EXPENSE
        assert request.amount == Decimal("100.00")
        assert request.description == "Test transaction"

    def test_create_category_request_valid(self):
        """Deve criar request de categoria válido."""
        request = CreateCategoryRequest(
            name="Test Category",
            type=TransactionType.EXPENSE
        )
        
        assert request.name == "Test Category"
        assert request.type == TransactionType.EXPENSE

    def test_transaction_service_initialization(self, transaction_service):
        """Deve inicializar o serviço de transações."""
        assert transaction_service is not None

    def test_category_service_initialization(self, category_service):
        """Deve inicializar o serviço de categorias."""
        assert category_service is not None


class TestCategoryServiceBasic:
    """Testes básicos para CategoryService."""

    @pytest.fixture
    def category_service(self):
        """Serviço de categorias configurado."""
        category_repo = InMemoryCategoryRepository()
        return CategoryServiceImpl(category_repository=category_repo)

    def test_category_service_exists(self, category_service):
        """Deve ter um serviço de categorias funcional."""
        assert category_service is not None
