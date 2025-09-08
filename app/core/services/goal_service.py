"""
Implementação do serviço de Metas Financeiras.

Este módulo contém a lógica de negócio para gestão de metas financeiras.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from app.core.domain.goal import Goal
from app.core.domain.exceptions import (
    GoalNotFoundError,
    InvalidGoalAmountError,
    GoalAlreadyCompletedError,
    GoalDeadlinePassedError,
)
from app.core.ports.goal import GoalRepository, GoalService


class GoalServiceImpl(GoalService):
    """Implementação do serviço de metas."""

    def __init__(self, goal_repository: GoalRepository):
        self._goal_repo = goal_repository

    async def create_goal(
        self,
        user_id: UUID,
        name: str,
        target_amount: Decimal,
        deadline: datetime,
        description: Optional[str] = None,
    ) -> Goal:
        """Cria uma nova meta financeira."""
        if target_amount <= 0:
            raise InvalidGoalAmountError(float(target_amount))

        if deadline <= datetime.utcnow():
            raise GoalDeadlinePassedError("A data limite deve ser no futuro.")

        goal = Goal(
            user_id=str(user_id),
            name=name,
            description=description,
            target_amount=target_amount,
            deadline=deadline,
        )
        return await self._goal_repo.create(goal)

    async def get_goal_by_id(
        self, goal_id: str, user_id: UUID
    ) -> Optional[Goal]:
        """Busca meta por ID."""
        goal = await self._goal_repo.get_by_id(goal_id, user_id)
        if not goal:
            raise GoalNotFoundError(goal_id, str(user_id))
        return goal

    async def list_goals(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> List[Goal]:
        """Lista as metas do usuário."""
        return await self._goal_repo.get_by_user_id(
            user_id=user_id, limit=limit, offset=offset
        )

    async def update_goal(
        self,
        goal_id: str,
        user_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        target_amount: Optional[Decimal] = None,
        deadline: Optional[datetime] = None,
    ) -> Goal:
        """Atualiza os detalhes de uma meta."""
        goal = await self.get_goal_by_id(goal_id, user_id)
        if not goal:
            raise GoalNotFoundError(goal_id, str(user_id))

        if goal.current_amount >= goal.target_amount:
            raise GoalAlreadyCompletedError(goal_id)

        if name is not None:
            goal.name = name
        if description is not None:
            goal.description = description
        if target_amount is not None:
            if target_amount <= 0:
                raise InvalidGoalAmountError(float(target_amount))
            if goal.current_amount > target_amount:
                raise ValueError(
                    "O novo valor alvo não pode ser menor que o valor atual."
                )
            goal.target_amount = target_amount
        if deadline is not None:
            if deadline <= datetime.utcnow():
                raise GoalDeadlinePassedError(
                    "A data limite deve ser no futuro."
                )
            goal.deadline = deadline

        goal.updated_at = datetime.utcnow()
        return await self._goal_repo.update(goal)

    async def delete_goal(self, goal_id: str, user_id: UUID) -> None:
        """Exclui uma meta."""
        if not await self._goal_repo.delete(goal_id, user_id):
            raise GoalNotFoundError(goal_id, str(user_id))

    async def add_contribution(
        self, goal_id: str, user_id: UUID, amount: Decimal
    ) -> Goal:
        """Adiciona uma contribuição a uma meta."""
        goal = await self.get_goal_by_id(goal_id, user_id)
        if not goal:
            raise GoalNotFoundError(goal_id, str(user_id))

        if goal.current_amount >= goal.target_amount:
            raise GoalAlreadyCompletedError(goal_id)

        goal.add_contribution(amount)
        return await self._goal_repo.update(goal)