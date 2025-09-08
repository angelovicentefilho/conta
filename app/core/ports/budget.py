from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from app.core.domain.budget import Budget


class BudgetRepository(ABC):
    """Interface para repositório de orçamentos."""

    @abstractmethod
    async def upsert(self, budget: Budget) -> Budget:
        """Cria ou atualiza um orçamento."""
        pass

    @abstractmethod
    async def get_by_id(
        self, budget_id: str, user_id: UUID
    ) -> Optional[Budget]:
        """Busca orçamento por ID."""
        pass

    @abstractmethod
    async def get_by_user_and_month(
        self, user_id: UUID, month: datetime
    ) -> List[Budget]:
        """Lista orçamentos de um usuário para um mês específico."""
        pass

    @abstractmethod
    async def delete(self, budget_id: str, user_id: UUID) -> bool:
        """Exclui um orçamento."""
        pass


class BudgetService(ABC):
    """Interface para serviço de orçamentos."""

    @abstractmethod
    async def set_budget(
        self,
        user_id: UUID,
        category_id: UUID,
        amount: Decimal,
        month: datetime,
    ) -> Budget:
        """Define ou atualiza um orçamento para uma categoria em um mês."""
        pass

    @abstractmethod
    async def get_budgets_by_month(
        self, user_id: UUID, month: datetime
    ) -> List[dict]:
        """
        Lista os orçamentos de um mês, incluindo o valor gasto.
        Retorna uma lista de dicionários com dados do orçamento e de gastos.
        """
        pass

    @abstractmethod
    async def delete_budget(self, budget_id: str, user_id: UUID) -> None:
        """Exclui um orçamento."""
        pass