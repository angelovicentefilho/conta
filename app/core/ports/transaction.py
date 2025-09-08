"""
Ports (interfaces) para Transação e Categoria.

Este módulo define as interfaces que devem ser implementadas pelos
adaptadores para transações e categorias.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.core.domain.transaction import (
    Transaction, Category, TransactionType
)


class TransactionRepository(ABC):
    """Interface para repositório de transações."""
    
    @abstractmethod
    async def create(self, transaction: Transaction) -> Transaction:
        """Cria uma nova transação."""
        pass
    
    @abstractmethod
    async def get_by_id(
        self, transaction_id: UUID, user_id: UUID
    ) -> Optional[Transaction]:
        """Busca transação por ID validando propriedade."""
        pass
    
    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: UUID,
        account_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        transaction_type: Optional[TransactionType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Transaction]:
        """Lista transações do usuário com filtros opcionais."""
        pass
    
    @abstractmethod
    async def update(self, transaction: Transaction) -> Transaction:
        """Atualiza uma transação existente."""
        pass
    
    @abstractmethod
    async def delete(self, transaction_id: UUID, user_id: UUID) -> bool:
        """Remove transação (soft delete)."""
        pass
    
    @abstractmethod
    async def count_by_user_id(self, user_id: UUID) -> int:
        """Conta total de transações ativas do usuário."""
        pass
    
    @abstractmethod
    async def count_by_category_id(self, category_id: UUID) -> int:
        """Conta transações que usam uma categoria."""
        pass
    
    @abstractmethod
    async def get_balance_by_account(
        self, account_id: UUID, user_id: UUID
    ) -> float:
        """Calcula saldo atual de uma conta baseado nas transações."""
        pass


class CategoryRepository(ABC):
    """Interface para repositório de categorias."""
    
    @abstractmethod
    async def create(self, category: Category) -> Category:
        """Cria uma nova categoria."""
        pass
    
    @abstractmethod
    async def get_by_id(
        self, category_id: UUID, user_id: Optional[UUID] = None
    ) -> Optional[Category]:
        """Busca categoria por ID (sistema ou usuário)."""
        pass
    
    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: UUID,
        category_type: Optional[TransactionType] = None,
        include_system: bool = True
    ) -> List[Category]:
        """Lista categorias do usuário + sistema."""
        pass
    
    @abstractmethod
    async def get_by_name_and_user(
        self, name: str, user_id: UUID, category_type: TransactionType
    ) -> Optional[Category]:
        """Busca categoria por nome, usuário e tipo."""
        pass
    
    @abstractmethod
    async def update(self, category: Category) -> Category:
        """Atualiza uma categoria existente."""
        pass
    
    @abstractmethod
    async def delete(self, category_id: UUID, user_id: UUID) -> bool:
        """Remove categoria (soft delete)."""
        pass
    
    @abstractmethod
    async def get_system_categories(
        self, category_type: Optional[TransactionType] = None
    ) -> List[Category]:
        """Lista categorias do sistema."""
        pass
    
    @abstractmethod
    async def initialize_system_categories(self) -> None:
        """Inicializa categorias padrão do sistema."""
        pass


class TransactionService(ABC):
    """Interface para serviço de transações."""
    
    @abstractmethod
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
        recurrence_frequency: Optional[str] = None
    ) -> Transaction:
        """Cria uma nova transação e atualiza saldo da conta."""
        pass
    
    @abstractmethod
    async def get_transaction_by_id(
        self, transaction_id: UUID, user_id: UUID
    ) -> Transaction:
        """Busca transação por ID."""
        pass
    
    @abstractmethod
    async def list_transactions(
        self,
        user_id: UUID,
        account_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        transaction_type: Optional[TransactionType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Transaction]:
        """Lista transações com filtros."""
        pass
    
    @abstractmethod
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
        recurrence_frequency: Optional[str] = None
    ) -> Transaction:
        """Atualiza transação e recalcula saldos."""
        pass
    
    @abstractmethod
    async def delete_transaction(
        self, transaction_id: UUID, user_id: UUID
    ) -> None:
        """Remove transação e reverte saldo."""
        pass
    
    @abstractmethod
    async def duplicate_transaction(
        self, transaction_id: UUID, user_id: UUID, new_date: datetime
    ) -> Transaction:
        """Duplica uma transação com nova data."""
        pass


class CategoryService(ABC):
    """Interface para serviço de categorias."""
    
    @abstractmethod
    async def create_category(
        self, user_id: UUID, name: str, category_type: TransactionType
    ) -> Category:
        """Cria uma categoria personalizada do usuário."""
        pass
    
    @abstractmethod
    async def get_category_by_id(
        self, category_id: UUID, user_id: Optional[UUID] = None
    ) -> Category:
        """Busca categoria por ID."""
        pass
    
    @abstractmethod
    async def list_categories(
        self,
        user_id: UUID,
        category_type: Optional[TransactionType] = None
    ) -> List[Category]:
        """Lista categorias disponíveis para o usuário."""
        pass
    
    @abstractmethod
    async def update_category(
        self, category_id: UUID, user_id: UUID, name: str
    ) -> Category:
        """Atualiza nome de categoria personalizada."""
        pass
    
    @abstractmethod
    async def delete_category(
        self, category_id: UUID, user_id: UUID
    ) -> None:
        """Remove categoria se não estiver em uso."""
        pass
    
    @abstractmethod
    async def initialize_default_categories(self) -> None:
        """Inicializa categorias padrão do sistema."""
        pass
