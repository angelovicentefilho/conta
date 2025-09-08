"""
Interfaces (Ports) para o domínio de Conta Financeira.

Define os contratos que devem ser implementados pelos adaptadores
para persistência e outras operações relacionadas às contas.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.core.domain.account import Account


class AccountRepository(ABC):
    """Interface para repositório de contas financeiras."""
    
    @abstractmethod
    async def create(self, account: Account) -> Account:
        """
        Cria uma nova conta no repositório.
        
        Args:
            account: Instância da conta a ser criada
            
        Returns:
            Account: Conta criada com ID gerado
            
        Raises:
            AccountAlreadyExistsError: Se conta com mesmo nome já existe
                para o usuário
        """
        pass
    
    @abstractmethod
    async def get_by_id(
        self, account_id: UUID, user_id: UUID
    ) -> Optional[Account]:
        """
        Busca conta por ID e valida propriedade pelo usuário.
        
        Args:
            account_id: ID da conta
            user_id: ID do usuário proprietário
            
        Returns:
            Account ou None se não encontrada ou não pertencer ao usuário
        """
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[Account]:
        """
        Lista todas as contas ativas de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de contas do usuário ordenadas (principal primeiro,
            depois alfabética)
        """
        pass
    
    @abstractmethod
    async def get_by_name_and_user(
        self, name: str, user_id: UUID
    ) -> Optional[Account]:
        """
        Busca conta por nome e usuário (para validar unicidade).
        
        Args:
            name: Nome da conta
            user_id: ID do usuário
            
        Returns:
            Account ou None se não encontrada
        """
        pass
    
    @abstractmethod
    async def get_primary_account(self, user_id: UUID) -> Optional[Account]:
        """
        Busca a conta principal do usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Account principal ou None se não houver
        """
        pass
    
    @abstractmethod
    async def update(self, account: Account) -> Account:
        """
        Atualiza uma conta existente.
        
        Args:
            account: Conta com dados atualizados
            
        Returns:
            Account: Conta atualizada
            
        Raises:
            AccountNotFoundError: Se conta não existir
        """
        pass
    
    @abstractmethod
    async def delete(self, account_id: UUID, user_id: UUID) -> bool:
        """
        Remove uma conta (soft delete).
        
        Args:
            account_id: ID da conta
            user_id: ID do usuário proprietário
            
        Returns:
            bool: True se removida com sucesso
            
        Raises:
            AccountNotFoundError: Se conta não existir
            AccountHasTransactionsError: Se conta possuir transações
        """
        pass
    
    @abstractmethod
    async def set_primary_account(
        self, account_id: UUID, user_id: UUID
    ) -> None:
        """
        Define uma conta como principal, removendo status das outras.
        
        Args:
            account_id: ID da conta a ser definida como principal
            user_id: ID do usuário proprietário
            
        Raises:
            AccountNotFoundError: Se conta não existir
        """
        pass
    
    @abstractmethod
    async def count_user_accounts(self, user_id: UUID) -> int:
        """
        Conta quantas contas ativas o usuário possui.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            int: Número de contas ativas
        """
        pass


class AccountService(ABC):
    """Interface para serviço de gestão de contas."""
    
    @abstractmethod
    async def create_account(
        self,
        user_id: UUID,
        name: str,
        account_type: str,
        balance: float = 0.0,
        is_primary: bool = False
    ) -> Account:
        """
        Cria uma nova conta financeira.
        
        Args:
            user_id: ID do usuário proprietário
            name: Nome da conta
            account_type: Tipo da conta
            balance: Saldo inicial (padrão 0.0)
            is_primary: Se deve ser conta principal
            
        Returns:
            Account: Conta criada
            
        Raises:
            AccountNameNotUniqueError: Se nome já existe
            InvalidAccountTypeError: Se tipo inválido
            InvalidBalanceError: Se saldo inválido para o tipo
        """
        pass
    
    @abstractmethod
    async def get_user_accounts(self, user_id: UUID) -> List[Account]:
        """
        Lista contas do usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de contas ordenadas
        """
        pass
    
    @abstractmethod
    async def get_account(self, account_id: UUID, user_id: UUID) -> Account:
        """
        Obtém conta específica do usuário.
        
        Args:
            account_id: ID da conta
            user_id: ID do usuário
            
        Returns:
            Account: Dados da conta
            
        Raises:
            AccountNotFoundError: Se não encontrada
        """
        pass
    
    @abstractmethod
    async def update_account(
        self,
        account_id: UUID,
        user_id: UUID,
        name: Optional[str] = None,
        account_type: Optional[str] = None,
        balance: Optional[float] = None
    ) -> Account:
        """
        Atualiza dados de uma conta.
        
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
        """
        pass
    
    @abstractmethod
    async def delete_account(self, account_id: UUID, user_id: UUID) -> None:
        """
        Remove uma conta.
        
        Args:
            account_id: ID da conta
            user_id: ID do usuário
            
        Raises:
            AccountNotFoundError: Se não encontrada
            CannotDeleteLastAccountError: Se é a última conta
            AccountHasTransactionsError: Se possui transações
        """
        pass
    
    @abstractmethod
    async def set_primary_account(self, account_id: UUID, user_id: UUID) -> Account:
        """
        Define conta como principal.
        
        Args:
            account_id: ID da conta
            user_id: ID do usuário
            
        Returns:
            Account: Conta atualizada como principal
            
        Raises:
            AccountNotFoundError: Se não encontrada
        """
        pass
