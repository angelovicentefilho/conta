from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field

from app.core.domain.user import User
from app.core.services.budget_service import BudgetService
from app.adapters.inbound.auth_middleware import get_current_user
from app.adapters.inbound.dependencies import BudgetServiceDep


router = APIRouter(prefix="/api/v1/budgets", tags=["Budgets"])


class BudgetResponse(BaseModel):
    id: str
    category_id: UUID = Field(alias="categoryId")
    category_name: str = Field(alias="categoryName")
    amount: Decimal
    month: str
    created_at: datetime = Field(alias="createdAt")

    model_config = {
        "populate_by_name": True,
        "json_encoders": {Decimal: str, UUID: str}
    }


class BudgetCreateUpdateRequest(BaseModel):
    category_id: UUID = Field(..., alias="categoryId")
    amount: Decimal
    month: str  # YYYY-MM


@router.post(
    "/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED
)
async def create_or_update_budget(
    request: BudgetCreateUpdateRequest,
    current_user: User = Depends(get_current_user),
    budget_service: BudgetService = Depends(BudgetServiceDep),
) -> BudgetResponse:
    month_dt = datetime.strptime(request.month, "%Y-%m")
    budget = await budget_service.set_budget(
        user_id=UUID(current_user.id),
        category_id=request.category_id,
        amount=request.amount,
        month=month_dt,
    )
    # This is a placeholder, the service should return a dict with categoryName
    return BudgetResponse(
        id=budget.id,
        categoryId=budget.category_id,
        categoryName="Placeholder",
        amount=budget.amount,
        month=budget.month.strftime("%Y-%m"),
        createdAt=budget.created_at,
    )


@router.get("/", response_model=List[BudgetResponse])
async def list_budgets(
    month: str = Query(..., regex=r"^\d{4}-\d{2}$"),
    current_user: User = Depends(get_current_user),
    budget_service: BudgetService = Depends(BudgetServiceDep),
) -> List[BudgetResponse]:
    month_dt = datetime.strptime(month, "%Y-%m")
    budgets = await budget_service.get_budgets_by_month(
        UUID(current_user.id), month_dt
    )
    # This is a placeholder, the service should return a dict with categoryName
    return [
        BudgetResponse(
            id=b["id"],
            categoryId=b["category_id"],
            categoryName="Placeholder",
            amount=b["amount"],
            month=b["month"].strftime("%Y-%m"),
            createdAt=b["created_at"],
        )
        for b in budgets
    ]


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    budget_service: BudgetService = Depends(BudgetServiceDep),
) -> None:
    await budget_service.delete_budget(budget_id, UUID(current_user.id))
