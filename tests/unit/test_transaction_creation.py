"""
Testes unitários para criação de transações.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.core.domain.user import User
from app.core.domain.account import Account, AccountType
from app.core.domain.transaction import (
    Category, TransactionType, RecurrenceType
)
from app.core.services.transaction_service import TransactionServiceImpl
from app.adapters.outbound.memory_repositories import (
    InMemoryTransactionRepository,
    InMemoryAccountRepository,
    InMemoryCategoryRepository
)
from app.core.exceptions import (
    AccountNotFoundError,
    CategoryNotFoundError
)
from app.adapters.inbound.requests.transaction_requests import (
    CreateTransactionRequest
)


class TestTransactionCreation:
    """Testes para criação de transações."""

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

    async def test_create_transaction_success(
        self, service, user, account, category, category_repo
    ):
        """Testa criação bem-sucedida de transação."""
        category.type = TransactionType.INCOME
        await category_repo.create(category)
        await service._account_repo.create(account)
        
        request = CreateTransactionRequest(
            account_id=account.id,
            category_id=category.id,
            type=TransactionType.INCOME,
            amount=Decimal("100.00"),
            description="Test transaction",
            date=datetime.utcnow()
        )

        result = await service.create_transaction(
            user_id=UUID(user.id),
            account_id=request.account_id,
            category_id=request.category_id,
            transaction_type=request.type,
            amount=float(request.amount),
            description=request.description,
            date=request.date
        )

        assert result is not None
        assert result.user_id == UUID(user.id)
        assert result.account_id == request.account_id
        assert result.category_id == request.category_id
        assert result.amount == request.amount
        assert result.description == request.description
        assert result.type == request.type

        # Verificar se o saldo da conta foi atualizado
        updated_account = await service._account_repo.get_by_id(
            account.id, UUID(user.id)
        )
        assert updated_account.balance == request.amount

    async def test_create_recurring_transaction(
        self, service, user, account, category, category_repo
    ):
        """Testa criação de transação recorrente."""
        category.type = TransactionType.INCOME
        await category_repo.create(category)
        await service._account_repo.create(account)
        
        request = CreateTransactionRequest(
            account_id=account.id,
            category_id=category.id,
            type=TransactionType.INCOME,
            amount=Decimal("500.00"),
            description="Salary",
            date=datetime.utcnow(),
            is_recurring=True,
            recurrence_frequency=RecurrenceType.MONTHLY.value
        )

        result = await service.create_transaction(
            user_id=UUID(user.id),
            account_id=request.account_id,
            category_id=request.category_id,
            transaction_type=request.type,
            amount=float(request.amount),
            description=request.description,
            date=request.date,
            is_recurring=request.is_recurring,
            recurrence_frequency=request.recurrence_frequency
        )

        assert result is not None
        assert result.is_recurring is True
        assert result.recurrence_frequency == RecurrenceType.MONTHLY

    async def test_create_transaction_account_not_found(
        self, service, user, category, category_repo
    ):
        """Testa criação de transação com conta inexistente."""
        await category_repo.create(category)
        request = CreateTransactionRequest(
            account_id=uuid4(),
            category_id=category.id,
            type=TransactionType.EXPENSE,
            amount=Decimal("100.00"),
            description="Test",
            date=datetime.utcnow()
        )

        with pytest.raises(AccountNotFoundError):
            await service.create_transaction(
                user_id=UUID(user.id),
                account_id=request.account_id,
                category_id=request.category_id,
                transaction_type=request.type,
                amount=float(request.amount),
                description=request.description,
                date=request.date
            )

    async def test_create_transaction_category_not_found(
        self, service, user, account
    ):
        """Testa criação de transação com categoria inexistente."""
        await service._account_repo.create(account)
        request = CreateTransactionRequest(
            account_id=account.id,
            category_id=uuid4(),
            type=TransactionType.EXPENSE,
            amount=Decimal("100.00"),
            description="Test",
            date=datetime.utcnow()
        )

        with pytest.raises(CategoryNotFoundError):
            await service.create_transaction(
                user_id=UUID(user.id),
                account_id=request.account_id,
                category_id=request.category_id,
                transaction_type=request.type,
                amount=float(request.amount),
                description=request.description,
                date=request.date
            )
