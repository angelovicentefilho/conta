"""
Testes abrangentes para TransactionService - Parte 2: Update e Delete.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from app.adapters.outbound.memory_repositories import (
    InMemoryAccountRepository,
    InMemoryCategoryRepository,
    InMemoryTransactionRepository,
)
from app.core.domain.account import Account, AccountType
from app.core.domain.exceptions import (
    AccountNotFoundError,
    CategoryNotFoundError,
    InvalidTransactionAmountError,
    TransactionNotFoundError,
)
from app.core.domain.transaction import (
    Category,
    RecurrenceType,
    TransactionType,
)
from app.core.domain.user import User
from app.core.services.transaction_service import TransactionServiceImpl


class TestTransactionServiceUpdateDelete:
    """Testes para update e delete de transações."""

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
            is_active=True,
        )

    @pytest.fixture
    def account(self, user):
        """Conta de teste."""
        return Account(
            id=uuid4(),
            user_id=UUID(user.id),
            name="Test Account",
            type=AccountType.CHECKING,
            balance=Decimal("5000.00"),  # Saldo alto para evitar negativo
        )

    @pytest.fixture
    def account2(self, user):
        """Segunda conta de teste."""
        return Account(
            id=uuid4(),
            user_id=UUID(user.id),
            name="Second Account",
            type=AccountType.SAVINGS,
            balance=Decimal("2000.00"),
        )

    @pytest.fixture
    def income_category(self, user):
        """Categoria de receita."""
        return Category(
            id=uuid4(),
            user_id=UUID(user.id),
            name="Salary",
            type=TransactionType.INCOME,
        )

    @pytest.fixture
    def expense_category(self, user):
        """Categoria de despesa."""
        return Category(
            id=uuid4(),
            user_id=UUID(user.id),
            name="Food",
            type=TransactionType.EXPENSE,
        )

    @pytest.fixture
    def expense_category2(self, user):
        """Segunda categoria de despesa."""
        return Category(
            id=uuid4(),
            user_id=UUID(user.id),
            name="Transport",
            type=TransactionType.EXPENSE,
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
    def service(self, transaction_repo, category_repo, account_repo):
        """Serviço de transações configurado."""
        return TransactionServiceImpl(
            transaction_repository=transaction_repo,
            category_repository=category_repo,
            account_repository=account_repo,
        )

    async def test_update_transaction_amount(
        self, service, user, account, income_category, category_repo
    ):
        """Testa atualização do valor da transação."""
        await category_repo.create(income_category)
        await service._account_repo.create(account)

        # Criar transação
        transaction = await service.create_transaction(
            user_id=UUID(user.id),
            account_id=account.id,
            category_id=income_category.id,
            transaction_type=TransactionType.INCOME,
            amount=500.0,
            description="Original amount",
            date=datetime.utcnow(),
        )

        # Atualizar valor
        updated = await service.update_transaction(
            transaction_id=transaction.id, user_id=UUID(user.id), amount=750.0
        )

        assert updated.amount == Decimal("750.00")
        assert (
            updated.description == "Original amount"
        )  # Outros campos inalterados

    async def test_update_transaction_description(
        self, service, user, account, income_category, category_repo
    ):
        """Testa atualização da descrição."""
        await category_repo.create(income_category)
        await service._account_repo.create(account)

        # Criar transação
        transaction = await service.create_transaction(
            user_id=UUID(user.id),
            account_id=account.id,
            category_id=income_category.id,
            transaction_type=TransactionType.INCOME,
            amount=500.0,
            description="Original description",
            date=datetime.utcnow(),
        )

        # Atualizar descrição
        updated = await service.update_transaction(
            transaction_id=transaction.id,
            user_id=UUID(user.id),
            description="Updated description",
        )

        assert updated.description == "Updated description"
        assert updated.amount == Decimal("500.00")  # Outros campos inalterados

    async def test_update_transaction_account(
        self, service, user, account, account2, income_category, category_repo
    ):
        """Testa mudança de conta da transação."""
        await category_repo.create(income_category)
        await service._account_repo.create(account)
        await service._account_repo.create(account2)

        # Criar transação na primeira conta
        transaction = await service.create_transaction(
            user_id=UUID(user.id),
            account_id=account.id,
            category_id=income_category.id,
            transaction_type=TransactionType.INCOME,
            amount=500.0,
            description="Test transaction",
            date=datetime.utcnow(),
        )

        # Mover para segunda conta
        updated = await service.update_transaction(
            transaction_id=transaction.id,
            user_id=UUID(user.id),
            account_id=account2.id,
        )

        assert updated.account_id == account2.id

    async def test_update_transaction_category(
        self,
        service,
        user,
        account,
        expense_category,
        expense_category2,
        category_repo,
    ):
        """Testa mudança de categoria da transação."""
        await category_repo.create(expense_category)
        await category_repo.create(expense_category2)

        # Criar conta do tipo CREDIT_CARD que permite saldo negativo
        account.type = AccountType.CREDIT_CARD
        await service._account_repo.create(account)

        # Criar transação
        transaction = await service.create_transaction(
            user_id=UUID(user.id),
            account_id=account.id,
            category_id=expense_category.id,
            transaction_type=TransactionType.EXPENSE,
            amount=100.0,
            description="Test expense",
            date=datetime.utcnow(),
        )

        # Mudar categoria
        updated = await service.update_transaction(
            transaction_id=transaction.id,
            user_id=UUID(user.id),
            category_id=expense_category2.id,
        )

        assert updated.category_id == expense_category2.id

    async def test_update_transaction_make_recurring(
        self, service, user, account, income_category, category_repo
    ):
        """Testa transformar transação em recorrente."""
        await category_repo.create(income_category)
        await service._account_repo.create(account)

        # Criar transação não recorrente
        transaction = await service.create_transaction(
            user_id=UUID(user.id),
            account_id=account.id,
            category_id=income_category.id,
            transaction_type=TransactionType.INCOME,
            amount=2000.0,
            description="Salary",
            date=datetime.utcnow(),
            is_recurring=False,
        )

        # Tornar recorrente
        updated = await service.update_transaction(
            transaction_id=transaction.id,
            user_id=UUID(user.id),
            is_recurring=True,
            recurrence_frequency=RecurrenceType.MONTHLY.value,
        )

        assert updated.is_recurring is True
        assert updated.recurrence_frequency == RecurrenceType.MONTHLY

    async def test_update_transaction_change_date(
        self, service, user, account, income_category, category_repo
    ):
        """Testa mudança da data da transação."""
        await category_repo.create(income_category)
        await service._account_repo.create(account)

        original_date = datetime(2024, 1, 1)
        # Data mais próxima para evitar erro de validação
        new_date = datetime.utcnow() - timedelta(days=5)

        # Criar transação
        transaction = await service.create_transaction(
            user_id=UUID(user.id),
            account_id=account.id,
            category_id=income_category.id,
            transaction_type=TransactionType.INCOME,
            amount=500.0,
            description="Test",
            date=original_date,
        )

        # Atualizar data
        updated = await service.update_transaction(
            transaction_id=transaction.id, user_id=UUID(user.id), date=new_date
        )

        assert updated.date == new_date

    # TESTES DE VALIDAÇÃO DE UPDATE

    async def test_update_transaction_not_found(self, service, user):
        """Testa erro ao atualizar transação inexistente."""
        with pytest.raises(TransactionNotFoundError):
            await service.update_transaction(
                transaction_id=uuid4(), user_id=UUID(user.id), amount=100.0
            )

    async def test_update_transaction_invalid_account(
        self, service, user, account, income_category, category_repo
    ):
        """Testa erro ao mover para conta inexistente."""
        await category_repo.create(income_category)
        await service._account_repo.create(account)

        # Criar transação
        transaction = await service.create_transaction(
            user_id=UUID(user.id),
            account_id=account.id,
            category_id=income_category.id,
            transaction_type=TransactionType.INCOME,
            amount=500.0,
            description="Test",
            date=datetime.utcnow(),
        )

        # Tentar mover para conta inexistente
        with pytest.raises(AccountNotFoundError):
            await service.update_transaction(
                transaction_id=transaction.id,
                user_id=UUID(user.id),
                account_id=uuid4(),  # Conta inexistente
            )

    async def test_update_transaction_invalid_category(
        self, service, user, account, income_category, category_repo
    ):
        """Testa erro ao mudar para categoria inexistente."""
        await category_repo.create(income_category)
        await service._account_repo.create(account)

        # Criar transação
        transaction = await service.create_transaction(
            user_id=UUID(user.id),
            account_id=account.id,
            category_id=income_category.id,
            transaction_type=TransactionType.INCOME,
            amount=500.0,
            description="Test",
            date=datetime.utcnow(),
        )

        # Tentar mudar para categoria inexistente
        with pytest.raises(CategoryNotFoundError):
            await service.update_transaction(
                transaction_id=transaction.id,
                user_id=UUID(user.id),
                category_id=uuid4(),  # Categoria inexistente
            )

    async def test_update_transaction_incompatible_category_type(
        self,
        service,
        user,
        account,
        income_category,
        expense_category,
        category_repo,
    ):
        """Testa erro ao mudar para categoria de tipo incompatível."""
        await category_repo.create(income_category)
        await category_repo.create(expense_category)
        await service._account_repo.create(account)

        # Criar transação de receita
        transaction = await service.create_transaction(
            user_id=UUID(user.id),
            account_id=account.id,
            category_id=income_category.id,
            transaction_type=TransactionType.INCOME,
            amount=500.0,
            description="Income",
            date=datetime.utcnow(),
        )

        # Tentar mudar para categoria de despesa sem mudar o tipo
        with pytest.raises(ValueError, match="Categoria é do tipo"):
            await service.update_transaction(
                transaction_id=transaction.id,
                user_id=UUID(user.id),
                category_id=expense_category.id,
                # Sem mudar transaction_type
            )

    async def test_update_transaction_invalid_amount(
        self, service, user, account, income_category, category_repo
    ):
        """Testa erro ao atualizar com valor inválido."""
        await category_repo.create(income_category)
        await service._account_repo.create(account)

        # Criar transação
        transaction = await service.create_transaction(
            user_id=UUID(user.id),
            account_id=account.id,
            category_id=income_category.id,
            transaction_type=TransactionType.INCOME,
            amount=500.0,
            description="Test",
            date=datetime.utcnow(),
        )

        # Tentar atualizar com valor inválido
        with pytest.raises(InvalidTransactionAmountError):
            await service.update_transaction(
                transaction_id=transaction.id,
                user_id=UUID(user.id),
                amount=0.0,  # Valor inválido
            )

    # TESTES DE DELETE

    async def test_delete_transaction_success(
        self, service, user, account, income_category, category_repo
    ):
        """Testa exclusão bem-sucedida de transação."""
        await category_repo.create(income_category)
        await service._account_repo.create(account)

        # Criar transação
        transaction = await service.create_transaction(
            user_id=UUID(user.id),
            account_id=account.id,
            category_id=income_category.id,
            transaction_type=TransactionType.INCOME,
            amount=500.0,
            description="To be deleted",
            date=datetime.utcnow(),
        )

        # Deletar
        await service.delete_transaction(transaction.id, UUID(user.id))

        # Verificar que foi deletada
        with pytest.raises(TransactionNotFoundError):
            await service.get_transaction_by_id(transaction.id, UUID(user.id))

    async def test_delete_transaction_not_found(self, service, user):
        """Testa erro ao deletar transação inexistente."""
        with pytest.raises(TransactionNotFoundError):
            await service.delete_transaction(uuid4(), UUID(user.id))
