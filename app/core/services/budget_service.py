from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from app.core.domain.budget import Budget
from app.core.ports.budget import BudgetRepository, BudgetService


class BudgetServiceImpl(BudgetService):
    """Implementação do serviço de orçamentos."""

    def __init__(self, budget_repository: BudgetRepository):
        self._budget_repo = budget_repository

    async def set_budget(
        self,
        user_id: UUID,
        category_id: UUID,
        amount: Decimal,
        month: datetime,
    ) -> Budget:
        """Define ou atualiza um orçamento para uma categoria em um mês."""
        # This is a placeholder implementation
        budget = Budget(
            user_id=user_id,
            category_id=category_id,
            amount=amount,
            month=month,
        )
        return await self._budget_repo.upsert(budget)

    async def get_budgets_by_month(
        self, user_id: UUID, month: datetime
    ) -> List[dict]:
        """
        Lista os orçamentos de um mês, incluindo o valor gasto.
        Retorna uma lista de dicionários com dados do orçamento e de gastos.
        """
        # This is a placeholder implementation
        budgets = await self._budget_repo.get_by_user_and_month(user_id, month)
        return [b.model_dump() for b in budgets]

    async def delete_budget(self, budget_id: str, user_id: UUID) -> None:
        """Exclui um orçamento."""
        # This is a placeholder implementation
        await self._budget_repo.delete(budget_id, user_id)
