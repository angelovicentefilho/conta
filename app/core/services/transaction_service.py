"""
Implementação dos serviços de Transação e Categoria.

Este módulo contém a lógica de negócio para gestão de transações
e categorias financeiras.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from app.core.domain.exceptions import (
    AccountNotFoundError,
    CannotDeleteSystemCategoryError,
    CategoryAlreadyExistsError,
    CategoryNameNotUniqueError,
    CategoryNotFoundError,
    InvalidTransactionAmountError,
    TransactionNotFoundError,
)
from app.core.domain.transaction import (
    Category,
    RecurrenceType,
    Transaction,
    TransactionType,
)
from app.core.ports.account import AccountRepository
from app.core.ports.transaction import CategoryRepository
from app.core.ports.transaction import CategoryService as CategoryServicePort
from app.core.ports.transaction import TransactionRepository
from app.core.ports.transaction import (
    TransactionService as TransactionServicePort,
)


class TransactionServiceImpl(TransactionServicePort):
    """Implementação do serviço de transações."""

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        category_repository: CategoryRepository,
        account_repository: AccountRepository,
    ):
        self._transaction_repo = transaction_repository
        self._category_repo = category_repository
        self._account_repo = account_repository

    async def create_transaction(
        self,
        user_id: UUID,
        account_id: UUID,
        category_id: UUID,
        transaction_type: TransactionType,
        amount: float,
        description: str,
        date: datetime,
        is_recurring: bool = False,
        recurrence_frequency: Optional[str] = None,
    ) -> Transaction:
        """Cria uma nova transação e atualiza saldo da conta."""
        # Validar se conta existe e pertence ao usuário
        account = await self._account_repo.get_by_id(account_id, user_id)
        if not account:
            raise AccountNotFoundError(str(account_id), str(user_id))

        # Validar se categoria existe e é acessível ao usuário
        category = await self._category_repo.get_by_id(category_id, user_id)
        if not category:
            raise CategoryNotFoundError(str(category_id), str(user_id))

        # Validar se tipo da categoria é compatível
        if category.type != transaction_type:
            raise ValueError(
                f"Categoria é do tipo {category.type}, "
                f"mas transação é do tipo {transaction_type}"
            )

        # Validar valor
        if amount <= 0:
            raise InvalidTransactionAmountError(amount)

        # Converter frequência de string para enum se fornecida
        frequency_enum = None
        if recurrence_frequency:
            try:
                frequency_enum = RecurrenceType(recurrence_frequency)
            except ValueError:
                raise ValueError(
                    f"Frequência inválida: {recurrence_frequency}"
                )

        # Criar transação
        transaction = Transaction(
            user_id=user_id,
            account_id=account_id,
            category_id=category_id,
            type=transaction_type,
            amount=Decimal(str(amount)),
            description=description,
            date=date,
            is_recurring=is_recurring,
            recurrence_frequency=frequency_enum,
        )

        # Salvar transação
        created_transaction = await self._transaction_repo.create(transaction)

        # Atualizar saldo da conta
        await self._update_account_balance(account_id, user_id)

        return created_transaction

    async def get_transaction_by_id(
        self, transaction_id: UUID, user_id: UUID
    ) -> Transaction:
        """Busca transação por ID."""
        transaction = await self._transaction_repo.get_by_id(
            transaction_id, user_id
        )
        if not transaction:
            raise TransactionNotFoundError(str(transaction_id), str(user_id))
        return transaction

    async def list_transactions(
        self,
        user_id: UUID,
        account_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        transaction_type: Optional[TransactionType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Transaction]:
        """Lista transações com filtros."""
        return await self._transaction_repo.get_by_user_id(
            user_id=user_id,
            account_id=account_id,
            category_id=category_id,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

    async def update_transaction(
        self,
        transaction_id: UUID,
        user_id: UUID,
        account_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        transaction_type: Optional[TransactionType] = None,
        amount: Optional[float] = None,
        description: Optional[str] = None,
        date: Optional[datetime] = None,
        is_recurring: Optional[bool] = None,
        recurrence_frequency: Optional[str] = None,
    ) -> Transaction:
        """Atualiza transação e recalcula saldos."""
        # Buscar transação existente
        transaction = await self.get_transaction_by_id(transaction_id, user_id)
        old_account_id = transaction.account_id

        # Validar nova conta se fornecida
        if account_id and account_id != transaction.account_id:
            account = await self._account_repo.get_by_id(account_id, user_id)
            if not account:
                raise AccountNotFoundError(str(account_id), str(user_id))

        # Validar nova categoria se fornecida
        if category_id and category_id != transaction.category_id:
            category = await self._category_repo.get_by_id(
                category_id, user_id
            )
            if not category:
                raise CategoryNotFoundError(str(category_id), str(user_id))

            # Verificar compatibilidade de tipo
            tx_type = transaction_type or transaction.type
            if category.type != tx_type:
                raise ValueError(
                    f"Categoria é do tipo {category.type}, "
                    f"mas transação é do tipo {tx_type}"
                )

        # Atualizar campos
        if account_id:
            transaction.update_account(account_id)
        if category_id:
            transaction.update_category(category_id)
        if transaction_type:
            transaction.type = transaction_type
        if amount is not None:
            if amount <= 0:
                raise InvalidTransactionAmountError(amount)
            transaction.update_amount(Decimal(str(amount)))
        if description:
            transaction.update_description(description)
        if date:
            transaction.update_date(date)
        if is_recurring is not None:
            if is_recurring and recurrence_frequency:
                frequency_enum = RecurrenceType(recurrence_frequency)
                transaction.make_recurring(frequency_enum)
            elif not is_recurring:
                transaction.remove_recurrence()

        # Salvar alterações
        updated_transaction = await self._transaction_repo.update(transaction)

        # Recalcular saldos das contas afetadas
        await self._update_account_balance(old_account_id, user_id)
        if account_id and account_id != old_account_id:
            await self._update_account_balance(account_id, user_id)

        return updated_transaction

    async def delete_transaction(
        self, transaction_id: UUID, user_id: UUID
    ) -> None:
        """Remove transação e reverte saldo."""
        # Buscar transação
        transaction = await self.get_transaction_by_id(transaction_id, user_id)
        account_id = transaction.account_id

        # Remover transação
        await self._transaction_repo.delete(transaction_id, user_id)

        # Recalcular saldo da conta
        await self._update_account_balance(account_id, user_id)

    async def duplicate_transaction(
        self, transaction_id: UUID, user_id: UUID, new_date: datetime
    ) -> Transaction:
        """Duplica uma transação com nova data."""
        # Buscar transação original
        original = await self.get_transaction_by_id(transaction_id, user_id)

        # Criar nova transação
        return await self.create_transaction(
            user_id=user_id,
            account_id=original.account_id,
            category_id=original.category_id,
            transaction_type=original.type,
            amount=float(original.amount),
            description=f"{original.description} (cópia)",
            date=new_date,
            is_recurring=original.is_recurring,
            recurrence_frequency=(
                original.recurrence_frequency.value
                if original.recurrence_frequency
                else None
            ),
        )

    async def _update_account_balance(
        self, account_id: UUID, user_id: UUID
    ) -> None:
        """Atualiza o saldo de uma conta baseado em suas transações."""
        # Calcular novo saldo baseado nas transações
        balance = await self._transaction_repo.get_balance_by_account(
            account_id, user_id
        )

        # Buscar conta e atualizar saldo
        account = await self._account_repo.get_by_id(account_id, user_id)
        if account:
            account.update_balance(Decimal(str(balance)))
            await self._account_repo.update(account)


class CategoryServiceImpl(CategoryServicePort):
    """Implementação do serviço de categorias."""

    def __init__(self, category_repository: CategoryRepository):
        self._category_repo = category_repository

    async def create_category(
        self, user_id: UUID, name: str, category_type: TransactionType
    ) -> Category:
        """Cria uma categoria personalizada do usuário."""
        # Verificar se já existe categoria com mesmo nome e tipo
        existing = await self._category_repo.get_by_name_and_user(
            name, user_id, category_type
        )
        if existing:
            raise CategoryAlreadyExistsError(name, str(user_id))

        # Criar nova categoria
        category = Category.create_user_category(user_id, name, category_type)
        return await self._category_repo.create(category)

    async def get_category_by_id(
        self, category_id: UUID, user_id: Optional[UUID] = None
    ) -> Category:
        """Busca categoria por ID."""
        category = await self._category_repo.get_by_id(category_id, user_id)
        if not category:
            raise CategoryNotFoundError(str(category_id), str(user_id))
        return category

    async def list_categories(
        self, user_id: UUID, category_type: Optional[TransactionType] = None
    ) -> List[Category]:
        """Lista categorias disponíveis para o usuário."""
        return await self._category_repo.get_by_user_id(
            user_id, category_type, include_system=True
        )

    async def update_category(
        self, category_id: UUID, user_id: UUID, name: str
    ) -> Category:
        """Atualiza nome de categoria personalizada."""
        # Buscar categoria
        category = await self.get_category_by_id(category_id, user_id)

        # Verificar se é categoria do sistema
        if category.is_system:
            raise CannotDeleteSystemCategoryError(str(category_id))

        # Verificar se pertence ao usuário
        if category.user_id != user_id:
            raise CategoryNotFoundError(str(category_id), str(user_id))

        # Verificar nome único
        existing = await self._category_repo.get_by_name_and_user(
            name, user_id, category.type
        )
        if existing and existing.id != category_id:
            raise CategoryNameNotUniqueError(
                name, str(user_id), category.type.value
            )

        # Atualizar nome
        category.update_name(name)
        return await self._category_repo.update(category)

    async def delete_category(self, category_id: UUID, user_id: UUID) -> None:
        """Remove categoria se não estiver em uso."""
        # Buscar categoria
        category = await self.get_category_by_id(category_id, user_id)

        # Verificar se é categoria do sistema
        if category.is_system:
            raise CannotDeleteSystemCategoryError(str(category_id))

        # Verificar se pertence ao usuário
        if category.user_id != user_id:
            raise CategoryNotFoundError(str(category_id), str(user_id))

        # Verificar se está em uso (implementação depende do repositório)
        # Por simplicidade, assumindo que o repositório faz essa verificação
        await self._category_repo.delete(category_id, user_id)

    async def initialize_default_categories(self) -> None:
        """Inicializa categorias padrão do sistema."""
        await self._category_repo.initialize_system_categories()
