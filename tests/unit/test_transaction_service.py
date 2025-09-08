"""
Testes unitários para TransactionServiceImpl e CategoryServiceImpl.

Valida a lógica de negócio para gestão de transações e categorias.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4, UUID

from app.core.domain.transaction import (
    Category, TransactionType, RecurrenceType,
    CreateTransactionRequest, CreateCategoryRequest
)
from app.core.domain.account import Account, AccountType
from app.core.domain.user import User
from app.core.domain.exceptions import (
    TransactionNotFoundError, CategoryNotFoundError,
    AccountNotFoundError, CategoryAlreadyExistsError,
    CannotDeleteSystemCategoryError
)
from app.core.services.transaction_service import (
    TransactionServiceImpl, CategoryServiceImpl
)
from app.adapters.outbound.memory_repositories import (
    InMemoryTransactionRepository, InMemoryCategoryRepository,
    InMemoryAccountRepository, InMemoryUserRepository
)


class TestTransactionService:
    """Testes para TransactionService."""

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
    async def user_repo(self, user):
        """Repositório de usuários em memória."""
        repo = InMemoryUserRepository()
        return repo

    @pytest.fixture
    def service(self, transaction_repo, category_repo, account_repo,
                user_repo):
        """Serviço de transações."""
        return TransactionServiceImpl(
            transaction_repository=transaction_repo,
            category_repository=category_repo,
            account_repository=account_repo
        )

    async def test_create_transaction_success(
        self, service, user, account, category, category_repo
    ):
        """Testa criação de transação com sucesso."""
        category.type = TransactionType.INCOME
        await category_repo.create(category)
        await service._account_repo.create(account)
        
        request = CreateTransactionRequest(
            account_id=account.id,
            category_id=category.id,
            type=TransactionType.INCOME,
            amount=Decimal("100.50"),
            description="Test transaction",
            date=datetime.utcnow()
        )

        transaction = await service.create_transaction(
            user_id=UUID(user.id),
            account_id=request.account_id,
            category_id=request.category_id,
            transaction_type=request.type,
            amount=float(request.amount),
            description=request.description,
            date=request.date,
            is_recurring=request.is_recurring,
            recurrence_frequency= (
                request.recurrence_frequency.value 
                if request.recurrence_frequency else None
            )
        )

        assert transaction.user_id == UUID(user.id)
        assert transaction.account_id == account.id
        assert transaction.category_id == category.id
        assert transaction.amount == Decimal("100.50")
        assert transaction.description == "Test transaction"
        assert not transaction.is_recurring

    async def test_create_recurring_transaction(
        self, service, user, account, category, category_repo
    ):
        """Testa criação de transação recorrente."""
        income_category = Category(
            id=uuid4(),
            user_id=UUID(user.id),
            name="Salary Category",
            type=TransactionType.INCOME
        )
        await category_repo.create(income_category)
        await service._account_repo.create(account)
        
        request = CreateTransactionRequest(
            account_id=account.id,
            category_id=income_category.id,
            type=TransactionType.INCOME,
            amount=Decimal("2000.00"),
            description="Salary",
            date=datetime.utcnow(),
            is_recurring=True,
            recurrence_frequency=RecurrenceType.MONTHLY
        )

        transaction = await service.create_transaction(
            user_id=UUID(user.id),
            account_id=request.account_id,
            category_id=request.category_id,
            transaction_type=request.type,
            amount=float(request.amount),
            description=request.description,
            date=request.date,
            is_recurring=request.is_recurring,
            recurrence_frequency= (
                request.recurrence_frequency.value 
                if request.recurrence_frequency else None
            )
        )

        assert transaction.is_recurring
        assert transaction.recurrence_frequency == RecurrenceType.MONTHLY

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


class TestCategoryService:
    """Testes para CategoryService."""

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
    def category_repo(self):
        """Repositório de categorias em memória."""
        return InMemoryCategoryRepository()

    @pytest.fixture
    async def user_repo(self, user):
        """Repositório de usuários em memória."""
        repo = InMemoryUserRepository()
        return repo

    @pytest.fixture
    def service(self, category_repo):
        """Serviço de categorias."""
        return CategoryServiceImpl(
            category_repository=category_repo,
        )

    async def test_create_category_success(self, service, user):
        """Testa criação de categoria com sucesso."""
        request = CreateCategoryRequest(
            name="Food",
            type=TransactionType.EXPENSE
        )

        category = await service.create_category(
            user_id=UUID(user.id), name=request.name, category_type=request.type
        )

        assert category.user_id == UUID(user.id)
        assert category.name == "Food"
        assert category.type == TransactionType.EXPENSE
        assert not category.is_system

    async def test_create_category_duplicate_name(self, service, user):
        """Testa criação de categoria com nome duplicado."""
        request = CreateCategoryRequest(
            name="Food",
            type=TransactionType.EXPENSE
        )

        await service.create_category(
            user_id=UUID(user.id), name=request.name, category_type=request.type
        )

        with pytest.raises(CategoryAlreadyExistsError):
            await service.create_category(
                user_id=UUID(user.id), name=request.name, category_type=request.type
            )

    async def test_get_user_categories(self, service, user, category_repo):
        """Testa busca de categorias do usuário."""
        await service.create_category(
            user_id=UUID(user.id), name="Food", category_type=TransactionType.EXPENSE
        )

        system_category = Category.create_system_category(
            "Salary", TransactionType.INCOME
        )
        await category_repo.create(system_category)

        categories = await service.list_categories(UUID(user.id))
        
        assert len(categories) == 2
        user_categories = [c for c in categories if not c.is_system]
        system_categories = [c for c in categories if c.is_system]
        
        assert len(user_categories) == 1
        assert len(system_categories) == 1

    async def test_delete_category_success(self, service, user):
        """Testa exclusão de categoria do usuário."""
        request = CreateCategoryRequest(
            name="To Delete",
            type=TransactionType.EXPENSE
        )

        category = await service.create_category(
            user_id=UUID(user.id), name=request.name, category_type=request.type
        )
        
        await service.delete_category(category.id, UUID(user.id))

        with pytest.raises(CategoryNotFoundError):
            await service.get_category_by_id(category.id, UUID(user.id))

    async def test_delete_system_category_fails(self, service, user, category_repo):
        """Testa que não é possível excluir categoria do sistema."""
        category = Category.create_system_category(
            "System Category", TransactionType.INCOME
        )
        await category_repo.create(category)

        with pytest.raises(CannotDeleteSystemCategoryError):
            await service.delete_category(category.id, UUID(user.id))
