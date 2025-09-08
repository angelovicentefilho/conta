"""
Serviço de Gestão de Contas Financeiras.

Implementa a lógica de negócio para criação, atualização, exclusão
e gestão de contas financeiras, seguindo as regras de domínio.
"""

from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from app.core.domain.account import Account, AccountType
from app.core.domain.exceptions import (
    AccountNameNotUniqueError,
    AccountNotFoundError,
    CannotDeleteLastAccountError,
    InvalidAccountTypeError,
    InvalidBalanceError,
)
from app.core.ports.account import AccountRepository


class AccountServiceImpl:
    """Implementação do serviço de gestão de contas."""
    
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository
    
    async def create_account(
        self,
        user_id: UUID,
        name: str,
        account_type: str,
        balance: float = 0.0,
        is_primary: bool = False
    ) -> Account:
        """
        Cria uma nova conta financeira com validações de negócio.
        
        Args:
            user_id: ID do usuário proprietário
            name: Nome da conta
            account_type: Tipo da conta
            balance: Saldo inicial
            is_primary: Se deve ser conta principal
            
        Returns:
            Account: Nova conta criada
            
        Raises:
            AccountNameNotUniqueError: Se nome já existe
            InvalidAccountTypeError: Se tipo inválido
            InvalidBalanceError: Se saldo inválido para o tipo
        """
        # Validar tipo de conta
        try:
            account_type_enum = AccountType(account_type)
        except ValueError:
            raise InvalidAccountTypeError(account_type)
        
        # Validar unicidade do nome
        existing_account = await self.account_repository.get_by_name_and_user(
            name, user_id
        )
        if existing_account:
            raise AccountNameNotUniqueError(name)
        
        # Validar saldo inicial conforme tipo de conta
        balance_decimal = Decimal(str(balance))
        if (balance_decimal < 0 and
                account_type_enum != AccountType.CREDIT_CARD):
            raise InvalidBalanceError(balance)
        
        # Se for definir como principal, remover status das outras contas
        if is_primary:
            await self._remove_primary_status_from_all(user_id)
        
        # Criar nova conta
        new_account = Account(
            user_id=user_id,
            name=name,
            type=account_type_enum,
            balance=balance_decimal,
            is_primary=is_primary
        )
        
        return await self.account_repository.create(new_account)
    
    async def get_user_accounts(self, user_id: UUID) -> List[Account]:
        """
        Lista todas as contas ativas do usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de contas ordenadas (principal primeiro, depois alfabética)
        """
        return await self.account_repository.get_by_user_id(user_id)
    
    async def get_account(self, account_id: UUID, user_id: UUID) -> Account:
        """
        Obtém conta específica validando propriedade.
        
        Args:
            account_id: ID da conta
            user_id: ID do usuário
            
        Returns:
            Account: Dados da conta
            
        Raises:
            AccountNotFoundError: Se não encontrada ou não pertencer ao usuário
        """
        account = await self.account_repository.get_by_id(account_id, user_id)
        if not account:
            raise AccountNotFoundError(str(account_id), str(user_id))
        
        return account
    
    async def update_account(
        self,
        account_id: UUID,
        user_id: UUID,
        name: Optional[str] = None,
        account_type: Optional[str] = None,
        balance: Optional[float] = None
    ) -> Account:
        """
        Atualiza dados de uma conta com validações.
        
        Args:
            account_id: ID da conta
            user_id: ID do usuário
            name: Novo nome (opcional)
            account_type: Novo tipo (opcional)
            balance: Novo saldo (opcional)
            
        Returns:
            Account: Conta atualizada
            
        Raises:
            AccountNotFoundError: Se não encontrada
            AccountNameNotUniqueError: Se nome já existe
            InvalidAccountTypeError: Se tipo inválido
            InvalidBalanceError: Se saldo inválido
        """
        # Buscar conta existente
        account = await self.get_account(account_id, user_id)
        
        # Validar e atualizar nome se fornecido
        if name is not None and name != account.name:
            name = name.strip()
            existing_account = (
                await self.account_repository.get_by_name_and_user(
                    name, user_id
                )
            )
            if existing_account and existing_account.id != account_id:
                raise AccountNameNotUniqueError(name)
            account.name = name
        
        # Validar e atualizar tipo se fornecido
        if account_type is not None:
            try:
                account_type_enum = AccountType(account_type)
                account.type = account_type_enum
            except ValueError:
                raise InvalidAccountTypeError(account_type)
        
        # Validar e atualizar saldo se fornecido
        if balance is not None:
            balance_decimal = Decimal(str(balance))
            if balance_decimal < 0 and not account.can_have_negative_balance():
                raise InvalidBalanceError(balance)
            account.update_balance(balance_decimal)
        
        return await self.account_repository.update(account)
    
    async def delete_account(self, account_id: UUID, user_id: UUID) -> None:
        """
        Remove uma conta com validações de negócio.
        
        Args:
            account_id: ID da conta
            user_id: ID do usuário
            
        Raises:
            AccountNotFoundError: Se não encontrada
            CannotDeleteLastAccountError: Se é a última conta
        """
        # Verificar se conta existe
        account = await self.get_account(account_id, user_id)
        
        # Verificar se não é a última conta do usuário
        account_count = await self.account_repository.count_user_accounts(
            user_id
        )
        if account_count <= 1:
            raise CannotDeleteLastAccountError()
        
        # Remover conta (soft delete)
        await self.account_repository.delete(account_id, user_id)
        
        # Se era conta principal, definir outra como principal
        if account.is_primary:
            await self._set_first_account_as_primary(user_id)
    
    async def set_primary_account(
        self, account_id: UUID, user_id: UUID
    ) -> Account:
        """
        Define uma conta como principal.
        
        Args:
            account_id: ID da conta
            user_id: ID do usuário
            
        Returns:
            Account: Conta atualizada como principal
            
        Raises:
            AccountNotFoundError: Se não encontrada
        """
        # Verificar se conta existe
        account = await self.get_account(account_id, user_id)
        
        # Remover status principal das outras contas
        await self._remove_primary_status_from_all(user_id)
        
        # Definir conta como principal
        account.set_as_primary()
        return await self.account_repository.update(account)
    
    async def _remove_primary_status_from_all(self, user_id: UUID) -> None:
        """Remove status de conta principal de todas as contas do usuário."""
        current_primary = await self.account_repository.get_primary_account(
            user_id
        )
        if current_primary:
            current_primary.remove_primary_status()
            await self.account_repository.update(current_primary)
    
    async def _set_first_account_as_primary(self, user_id: UUID) -> None:
        """Define a primeira conta ativa como principal."""
        accounts = await self.account_repository.get_by_user_id(user_id)
        if accounts:
            first_account = accounts[0]
            first_account.set_as_primary()
            await self.account_repository.update(first_account)
