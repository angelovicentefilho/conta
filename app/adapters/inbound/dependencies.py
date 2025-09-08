"""Módulo de dependências para injeção de dependências nos controladores."""

from typing import Annotated
from fastapi import Depends

from app.adapters.outbound.memory_repositories import (
    InMemoryGoalRepository,
    InMemoryBudgetRepository,
)
from app.core.ports.goal import GoalRepository, GoalService
from app.core.ports.budget import BudgetRepository, BudgetService
from app.core.services.goal_service import GoalServiceImpl
from app.core.services.budget_service import BudgetServiceImpl


def get_goal_repository() -> GoalRepository:
    """Obtém o repositório de metas."""
    return InMemoryGoalRepository()

def get_budget_repository() -> BudgetRepository:
    """Obtém o repositório de orçamentos."""
    return InMemoryBudgetRepository()


def get_goal_service(
    repo: GoalRepository = Depends(get_goal_repository),
) -> GoalService:
    """Obtém o serviço de metas."""
    return GoalServiceImpl(repo)


def get_budget_service(
    repo: BudgetRepository = Depends(get_budget_repository),
) -> BudgetService:
    """Obtém o serviço de orçamentos."""
    return BudgetServiceImpl(repo)


GoalServiceDep = Annotated[GoalService, Depends(get_goal_service)]
BudgetServiceDep = Annotated[BudgetService, Depends(get_budget_service)]