"""
Testes unitários para exclusão de transações.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.core.domain.user import User
from app.core.domain.account import Account, AccountType
from app.core.domain.transaction import Category, TransactionType
from app.core.services.transaction_service import TransactionServiceImpl
from app.adapters.outbound.memory_repositories import (
    InMemoryTransactionRepository,
    InMemoryAccountRepository,
    InMemoryCategoryRepository
)
from app.core.exceptions import TransactionNotFoundError
from app.adapters.inbound.requests.transaction_requests import (
    CreateTransactionRequest
)


class TestTransactionDeletion:
    """Testes para exclusão de transações."""

    @pytest.fixture
    def user(self):
        """Usuário de teste."""
        now = datetime.utcnow()
        return User(
            id=str(uuid4()),
            name="Test User",
            email="test@example.com",
            password_hash="Hashed_password1@",
            created_at=now,
            updated_at=now,
            is_active=True
        )

    @pytest.fixture
    def account(self, user):
        """Conta de teste."""
        return Account(
            id=uuid4(),
            user_id=UUID(user.id),
            name="Test Account",
            type=AccountType.CHECKING,
            balance=Decimal("0.00")
        )

    @pytest.fixture
    def category(self, user):
        """Categoria de teste."""
        return Category(
            id=uuid4(),
            user_id=UUID(user.id),
            name="Test Category",
            type=TransactionType.EXPENSE
        )

    @pytest.fixture
    def transaction_repo(self):
        """Repositório de transações em memória."""
        return InMemoryTransactionRepository()

    @pytest.fixture
    def category_repo(self):
        """Repositório de categorias em memória."""
        return InMemoryCategoryRepository()

    @pytest.fixture
    def account_repo(self):
        """Repositório de contas em memória."""
        return InMemoryAccountRepository()

    @pytest.fixture
    def service(self, transaction_repo, account_repo):
        """Serviço de transações configurado."""
        return TransactionServiceImpl(transaction_repo, account_repo)

    async def test_delete_transaction(
        self, service, user, account, category, category_repo
    ):
        """Testa exclusão de transação."""
        category.type = TransactionType.INCOME
        await category_repo.create(category)
        await service._account_repo.create(account)
        
        request = CreateTransactionRequest(
            account_id=account.id,
            category_id=category.id,
            type=TransactionType.INCOME,
            amount=Decimal("100.00"),
            description="To be deleted",
            date=datetime.utcnow()
        )

        transaction = await service.create_transaction(
            user_id=UUID(user.id),
            account_id=request.account_id,
            category_id=request.category_id,
            transaction_type=request.type,
            amount=float(request.amount),
            description=request.description,
            date=request.date
        )
        
        await service.delete_transaction(transaction.id, UUID(user.id))

        with pytest.raises(TransactionNotFoundError):
            await service.get_transaction_by_id(transaction.id, UUID(user.id))
