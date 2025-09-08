from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.adapters.inbound.auth_middleware import get_current_user
from app.adapters.inbound.dependencies import GoalServiceDep
from app.core.domain.user import User
from app.core.services.goal_service import GoalService

router = APIRouter(prefix="/api/v1/goals", tags=["Goals"])


class GoalResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    target_amount: Decimal
    current_amount: Decimal
    deadline: datetime
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "json_encoders": {Decimal: str},
    }


class GoalCreateRequest(BaseModel):
    name: str = Field(..., description="Nome da meta.")
    description: Optional[str] = Field(None, description="Descrição da meta.")
    target_amount: Decimal = Field(
        ..., alias="targetAmount", description="Valor alvo da meta."
    )
    deadline: datetime = Field(..., description="Prazo final da meta.")


class GoalUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="Novo nome da meta.")
    description: Optional[str] = Field(
        None, description="Nova descrição da meta."
    )
    target_amount: Optional[Decimal] = Field(
        None, alias="targetAmount", description="Novo valor alvo."
    )
    deadline: Optional[datetime] = Field(None, description="Novo prazo final.")


class ContributionRequest(BaseModel):
    amount: Decimal = Field(..., description="Valor da contribuição.")


@router.post(
    "/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED
)
async def create_goal(
    request: GoalCreateRequest,
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(GoalServiceDep),
) -> GoalResponse:
    """Cria uma nova meta financeira."""
    goal = await goal_service.create_goal(
        user_id=UUID(current_user.id), **request.model_dump()
    )
    return GoalResponse.model_validate(goal)


@router.get("/", response_model=List[GoalResponse])
async def list_goals(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(GoalServiceDep),
) -> List[GoalResponse]:
    """Lista as metas do usuário."""
    goals = await goal_service.list_goals(
        user_id=UUID(current_user.id), limit=limit, offset=offset
    )
    return [GoalResponse.model_validate(g) for g in goals]


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(GoalServiceDep),
) -> GoalResponse:
    """Obtém os detalhes de uma meta específica."""
    goal = await goal_service.get_goal_by_id(goal_id, UUID(current_user.id))
    if not goal:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Meta não encontrada.")
    return GoalResponse.model_validate(goal)


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    request: GoalUpdateRequest,
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(GoalServiceDep),
) -> GoalResponse:
    """Atualiza os detalhes de uma meta."""
    goal = await goal_service.update_goal(
        goal_id=goal_id,
        user_id=UUID(current_user.id),
        **request.model_dump(exclude_unset=True),
    )
    return GoalResponse.model_validate(goal)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(GoalServiceDep),
) -> None:
    """Exclui uma meta."""
    await goal_service.delete_goal(goal_id, UUID(current_user.id))


@router.post("/{goal_id}/contribute", response_model=GoalResponse)
async def add_contribution(
    goal_id: str,
    request: ContributionRequest,
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(GoalServiceDep),
) -> GoalResponse:
    """Adiciona uma contribuição a uma meta."""
    goal = await goal_service.add_contribution(
        goal_id=goal_id, user_id=UUID(current_user.id), amount=request.amount
    )
    return GoalResponse.model_validate(goal)
