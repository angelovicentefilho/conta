from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from bson import ObjectId


class Goal(BaseModel):
    """
    Entidade de domínio que representa uma meta financeira do usuário.
    """
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str = Field(..., alias="userId")
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    target_amount: Decimal = Field(..., alias="targetAmount", gt=Decimal(0))
    current_amount: Decimal = Field(
        default=Decimal("0"), alias="currentAmount", ge=Decimal(0)
    )
    deadline: datetime
    created_at: datetime = Field(
        default_factory=datetime.utcnow, alias="createdAt"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, alias="updatedAt"
    )

    model_config = {
        "populate_by_name": True,
        "json_encoders": {
            ObjectId: str,
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }
    }

    @field_validator('current_amount')
    @classmethod
    def validate_current_amount(cls, v: Decimal, info) -> Decimal:
        """Valida que o valor atual não ultrapasse o valor alvo."""
        if hasattr(info, 'data') and 'target_amount' in info.data:
            if v > info.data['target_amount']:
                raise ValueError(
                    'O valor atual não pode ser maior que o valor alvo.'
                )
        return v

    def add_contribution(self, amount: Decimal) -> None:
        """Adiciona uma contribuição à meta."""
        if amount <= 0:
            raise ValueError("O valor da contribuição deve ser positivo.")
        
        if self.current_amount + amount > self.target_amount:
            raise ValueError("A contribuição excede o valor alvo da meta.")

        self.current_amount += amount
        self.updated_at = datetime.utcnow()
