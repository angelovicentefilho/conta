"""
Testes unitários para busca e listagem de transações.
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
from app.adapters.inbound.requests.transaction_requests import (
    CreateTransactionRequest
)


class TestTransactionRetrieval:
    """Testes para busca e listagem de transações."""

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

    async def test_get_user_transactions(
        self, service, user, account, category, category_repo
    ):
        """Testa busca de transações do usuário."""
        income_category_1 = Category(
            id=uuid4(),
            user_id=UUID(user.id),
            name="Income Category 1",
            type=TransactionType.INCOME
        )
        await category_repo.create(income_category_1)
        await service._account_repo.create(account)
        
        request1 = CreateTransactionRequest(
            account_id=account.id,
            category_id=income_category_1.id,
            type=TransactionType.INCOME,
            amount=Decimal("50.00"),
            description="Transaction 1",
            date=datetime.utcnow()
        )
        
        expense_category = Category(
            id=uuid4(),
            user_id=UUID(user.id),
            name="Expense Category",
            type=TransactionType.EXPENSE
        )
        await category_repo.create(expense_category)
        
        request2 = CreateTransactionRequest(
            account_id=account.id,
            category_id=expense_category.id,
            type=TransactionType.EXPENSE,
            amount=Decimal("30.00"),
            description="Transaction 2",
            date=datetime.utcnow()
        )

        await service.create_transaction(
            user_id=UUID(user.id),
            account_id=request1.account_id,
            category_id=request1.category_id,
            transaction_type=request1.type,
            amount=float(request1.amount),
            description=request1.description,
            date=request1.date
        )
        await service.create_transaction(
            user_id=UUID(user.id),
            account_id=request2.account_id,
            category_id=request2.category_id,
            transaction_type=request2.type,
            amount=float(request2.amount),
            description=request2.description,
            date=request2.date
        )

        transactions = await service.list_transactions(UUID(user.id))
        assert len(transactions) == 2
