"""
Testes unitários para o serviço de contas financeiras.

Testa toda a lógica de negócio de criação, atualização, exclusão
e gestão de contas com validações e regras específicas.
"""

from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from app.core.domain.account import Account, AccountType
from app.core.domain.exceptions import (
    AccountNameNotUniqueError,
    AccountNotFoundError,
    CannotDeleteLastAccountError,
    InvalidAccountTypeError,
    InvalidBalanceError,
)
from app.core.services.account_service import AccountServiceImpl


class MockAccountRepository:
    """Mock do repositório de contas para testes."""

    def __init__(self):
        self.accounts = {}
        self.accounts_by_user = {}
        self.create_calls = []
        self.update_calls = []
        self.delete_calls = []

    async def create(self, account: Account) -> Account:
        self.create_calls.append(account)
        self.accounts[str(account.id)] = account
        return account

    async def get_by_id(self, account_id: UUID, user_id: UUID) -> Account:
        account = self.accounts.get(str(account_id))
        if account and account.user_id == user_id and account.is_active:
            return account
        return None

    async def get_by_user_id(self, user_id: UUID) -> list:
        return [
            account
            for account in self.accounts.values()
            if account.user_id == user_id and account.is_active
        ]

    async def get_by_name_and_user(self, name: str, user_id: UUID) -> Account:
        for account in self.accounts.values():
            if (
                account.name.lower() == name.lower()
                and account.user_id == user_id
                and account.is_active
            ):
                return account
        return None

    async def get_primary_account(self, user_id: UUID) -> Account:
        for account in self.accounts.values():
            if account.user_id == user_id and account.is_primary:
                return account
        return None

    async def update(self, account: Account) -> Account:
        self.update_calls.append(account)
        self.accounts[str(account.id)] = account
        return account

    async def delete(self, account_id: UUID, user_id: UUID) -> bool:
        self.delete_calls.append((account_id, user_id))
        account = await self.get_by_id(account_id, user_id)
        if account:
            account.deactivate()
            await self.update(account)
            return True
        return False

    async def set_primary_account(
        self, account_id: UUID, user_id: UUID
    ) -> None:
        # Implementação básica para testes
        pass

    async def count_user_accounts(self, user_id: UUID) -> int:
        active_accounts = await self.get_by_user_id(user_id)
        return len(active_accounts)


@pytest.fixture
def mock_repository():
    """Fixture para mock do repositório."""
    return MockAccountRepository()


@pytest.fixture
def account_service(mock_repository):
    """Fixture para serviço de contas com mock."""
    return AccountServiceImpl(mock_repository)


@pytest.fixture
def user_id():
    """Fixture para ID de usuário."""
    return uuid4()


@pytest.fixture
def other_user_id():
    """Fixture para ID de outro usuário."""
    return uuid4()


class TestAccountCreation:
    """Testes para criação de contas."""

    async def test_create_account_success(self, account_service, user_id):
        """Deve criar conta válida com sucesso."""
        account = await account_service.create_account(
            user_id=user_id,
            name="Conta Corrente",
            account_type="checking",
            balance=100.0,
            is_primary=True,
        )

        assert account.user_id == user_id
        assert account.name == "Conta Corrente"
        assert account.type == AccountType.CHECKING
        assert account.balance == Decimal("100.0")
        assert account.is_primary is True
        assert account.is_active is True

    async def test_create_account_with_zero_balance(
        self, account_service, user_id
    ):
        """Deve criar conta com saldo zero."""
        account = await account_service.create_account(
            user_id=user_id, name="Poupança", account_type="savings"
        )

        assert account.balance == Decimal("0.0")
        assert account.is_primary is False

    async def test_create_credit_card_with_negative_balance(
        self, account_service, user_id
    ):
        """Deve permitir saldo negativo para cartão de crédito."""
        account = await account_service.create_account(
            user_id=user_id,
            name="Cartão Visa",
            account_type="credit_card",
            balance=-500.0,
        )

        assert account.type == AccountType.CREDIT_CARD
        assert account.balance == Decimal("-500.0")

    async def test_create_account_invalid_type(self, account_service, user_id):
        """Deve falhar com tipo de conta inválido."""
        with pytest.raises(InvalidAccountTypeError):
            await account_service.create_account(
                user_id=user_id,
                name="Conta Inválida",
                account_type="invalid_type",
            )

    async def test_create_account_negative_balance_invalid(
        self, account_service, user_id
    ):
        """Deve falhar com saldo negativo para conta que não permite."""
        with pytest.raises(InvalidBalanceError):
            await account_service.create_account(
                user_id=user_id,
                name="Conta Corrente",
                account_type="checking",
                balance=-100.0,
            )

    async def test_create_account_duplicate_name(
        self, account_service, user_id, mock_repository
    ):
        """Deve falhar ao criar conta com nome duplicado."""
        # Criar primeira conta
        existing_account = Account(
            user_id=user_id,
            name="Conta Teste",
            type=AccountType.CHECKING,
            balance=Decimal("0.0"),
        )
        mock_repository.accounts[str(existing_account.id)] = existing_account

        # Tentar criar conta com mesmo nome
        with pytest.raises(AccountNameNotUniqueError):
            await account_service.create_account(
                user_id=user_id, name="Conta Teste", account_type="savings"
            )


class TestAccountRetrieval:
    """Testes para busca de contas."""

    async def test_get_user_accounts_empty(self, account_service, user_id):
        """Deve retornar lista vazia para usuário sem contas."""
        accounts = await account_service.get_user_accounts(user_id)
        assert accounts == []

    async def test_get_account_success(
        self, account_service, user_id, mock_repository
    ):
        """Deve buscar conta específica com sucesso."""
        account = Account(
            user_id=user_id,
            name="Conta Teste",
            type=AccountType.CHECKING,
            balance=Decimal("100.0"),
        )
        mock_repository.accounts[str(account.id)] = account

        result = await account_service.get_account(account.id, user_id)
        assert result.id == account.id
        assert result.name == "Conta Teste"

    async def test_get_account_not_found(self, account_service, user_id):
        """Deve falhar ao buscar conta inexistente."""
        fake_id = uuid4()
        with pytest.raises(AccountNotFoundError):
            await account_service.get_account(fake_id, user_id)

    async def test_get_account_wrong_user(
        self, account_service, user_id, other_user_id, mock_repository
    ):
        """Deve falhar ao buscar conta de outro usuário."""
        account = Account(
            user_id=other_user_id,
            name="Conta Outro User",
            type=AccountType.CHECKING,
            balance=Decimal("100.0"),
        )
        mock_repository.accounts[str(account.id)] = account

        with pytest.raises(AccountNotFoundError):
            await account_service.get_account(account.id, user_id)


class TestAccountUpdate:
    """Testes para atualização de contas."""

    async def test_update_account_name(
        self, account_service, user_id, mock_repository
    ):
        """Deve atualizar nome da conta."""
        account = Account(
            user_id=user_id,
            name="Nome Antigo",
            type=AccountType.CHECKING,
            balance=Decimal("100.0"),
        )
        mock_repository.accounts[str(account.id)] = account

        updated = await account_service.update_account(
            account_id=account.id, user_id=user_id, name="Nome Novo"
        )

        assert updated.name == "Nome Novo"
        assert updated.type == AccountType.CHECKING  # Mantém outros campos

    async def test_update_account_balance(
        self, account_service, user_id, mock_repository
    ):
        """Deve atualizar saldo da conta."""
        account = Account(
            user_id=user_id,
            name="Conta Teste",
            type=AccountType.CHECKING,
            balance=Decimal("100.0"),
        )
        mock_repository.accounts[str(account.id)] = account

        updated = await account_service.update_account(
            account_id=account.id, user_id=user_id, balance=250.50
        )

        assert updated.balance == Decimal("250.50")

    async def test_update_account_invalid_balance(
        self, account_service, user_id, mock_repository
    ):
        """Deve falhar ao definir saldo negativo inválido."""
        account = Account(
            user_id=user_id,
            name="Conta Corrente",
            type=AccountType.CHECKING,
            balance=Decimal("100.0"),
        )
        mock_repository.accounts[str(account.id)] = account

        with pytest.raises(InvalidBalanceError):
            await account_service.update_account(
                account_id=account.id, user_id=user_id, balance=-100.0
            )


class TestAccountDeletion:
    """Testes para exclusão de contas."""

    async def test_delete_account_success(
        self, account_service, user_id, mock_repository
    ):
        """Deve deletar conta quando há múltiplas contas."""
        # Criar duas contas
        account1 = Account(
            user_id=user_id, name="Conta 1", type=AccountType.CHECKING
        )
        account2 = Account(
            user_id=user_id, name="Conta 2", type=AccountType.SAVINGS
        )
        mock_repository.accounts[str(account1.id)] = account1
        mock_repository.accounts[str(account2.id)] = account2

        await account_service.delete_account(account1.id, user_id)

        # Verificar que delete foi chamado
        assert len(mock_repository.delete_calls) == 1
        assert mock_repository.delete_calls[0] == (account1.id, user_id)

    async def test_delete_last_account_fails(
        self, account_service, user_id, mock_repository
    ):
        """Deve falhar ao tentar deletar última conta."""
        account = Account(
            user_id=user_id, name="Única Conta", type=AccountType.CHECKING
        )
        mock_repository.accounts[str(account.id)] = account

        with pytest.raises(CannotDeleteLastAccountError):
            await account_service.delete_account(account.id, user_id)


class TestPrimaryAccount:
    """Testes para gestão de conta principal."""

    async def test_set_primary_account(
        self, account_service, user_id, mock_repository
    ):
        """Deve definir conta como principal."""
        account = Account(
            user_id=user_id,
            name="Nova Principal",
            type=AccountType.CHECKING,
            is_primary=False,
        )
        mock_repository.accounts[str(account.id)] = account

        result = await account_service.set_primary_account(account.id, user_id)

        assert result.is_primary is True

    async def test_set_primary_account_not_found(
        self, account_service, user_id
    ):
        """Deve falhar ao definir conta inexistente como principal."""
        fake_id = uuid4()
        with pytest.raises(AccountNotFoundError):
            await account_service.set_primary_account(fake_id, user_id)
