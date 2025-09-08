"""
Ports (interfaces) para Metas Financeiras.

Este módulo define as interfaces que devem ser implementadas pelos
adaptadores para gerenciamento de metas financeiras.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from app.core.domain.goal import Goal


class GoalRepository(ABC):
    """Interface para repositório de metas."""

    @abstractmethod
    async def create(self, goal: Goal) -> Goal:
        """Cria uma nova meta."""

    @abstractmethod
    async def get_by_id(self, goal_id: str, user_id: UUID) -> Optional[Goal]:
        """Busca meta por ID validando propriedade."""

    @abstractmethod
    async def get_by_user_id(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> List[Goal]:
        """Lista metas do usuário."""

    @abstractmethod
    async def update(self, goal: Goal) -> Goal:
        """Atualiza uma meta existente."""

    @abstractmethod
    async def delete(self, goal_id: str, user_id: UUID) -> bool:
        """Remove uma meta."""


class GoalService(ABC):
    """Interface para serviço de metas."""

    @abstractmethod
    async def create_goal(
        self,
        user_id: UUID,
        name: str,
        target_amount: Decimal,
        deadline: datetime,
        description: Optional[str] = None,
    ) -> Goal:
        """Cria uma nova meta financeira."""

    @abstractmethod
    async def get_goal_by_id(
        self, goal_id: str, user_id: UUID
    ) -> Optional[Goal]:
        """Busca meta por ID."""

    @abstractmethod
    async def list_goals(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> List[Goal]:
        """Lista as metas do usuário."""

    @abstractmethod
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

    @abstractmethod
    async def delete_goal(self, goal_id: str, user_id: UUID) -> None:
        """Exclui uma meta."""

    @abstractmethod
    async def add_contribution(
        self, goal_id: str, user_id: UUID, amount: Decimal
    ) -> Goal:
        """Adiciona uma contribuição a uma meta."""
