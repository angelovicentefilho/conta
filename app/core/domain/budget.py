from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Budget(BaseModel):
    """
    Entidade de domínio que representa um orçamento mensal para uma categoria.
    """
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: UUID = Field(..., alias="userId")
    category_id: UUID = Field(..., alias="categoryId")
    amount: Decimal = Field(..., gt=Decimal(0))
    month: datetime
    created_at: datetime = Field(
        default_factory=datetime.utcnow, alias="createdAt"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, alias="updatedAt"
    )

    model_config = {
        "populate_by_name": True,
        "json_encoders": {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v),
        }
    }
