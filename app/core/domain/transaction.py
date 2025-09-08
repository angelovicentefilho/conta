"""
Modelos de domínio para Transação Financeira.

Este módulo contém as entidades e value objects relacionados ao registro
de transações financeiras no sistema.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class TransactionType(str, Enum):
    """Tipos de transação financeira."""

    INCOME = "income"  # Receita
    EXPENSE = "expense"  # Despesa


class RecurrenceType(str, Enum):
    """Tipos de recorrência para transações."""

    WEEKLY = "weekly"  # Semanal
    MONTHLY = "monthly"  # Mensal
    QUARTERLY = "quarterly"  # Trimestral
    YEARLY = "yearly"  # Anual


class Transaction(BaseModel):
    """
    Entidade Transaction representando uma transação financeira.

    Contém as regras de negócio para registro e gestão de movimentações
    financeiras entre contas e categorias.
    """

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    account_id: UUID
    category_id: UUID
    type: TransactionType
    amount: Decimal = Field(gt=0)
    description: str = Field(min_length=1, max_length=500)
    date: datetime
    is_recurring: bool = False
    recurrence_frequency: Optional[RecurrenceType] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Valida o valor da transação."""
        if v <= 0:
            raise ValueError("Valor deve ser positivo")
        # Verifica se tem no máximo 2 casas decimais
        str_value = str(v)
        if "." in str_value:
            decimal_places = len(str_value.split(".")[1])
            if decimal_places > 2:
                raise ValueError("Valor deve ter no máximo 2 casas decimais")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Valida e limpa a descrição da transação."""
        v = v.strip()
        if not v:
            raise ValueError("Descrição não pode estar vazia")
        return v

    @field_validator("recurrence_frequency")
    @classmethod
    def validate_recurrence_frequency(
        cls, v: Optional[RecurrenceType], info: Any
    ) -> Optional[RecurrenceType]:
        """Valida frequência de recorrência baseada no campo is_recurring."""
        values = info.data if hasattr(info, "data") else {}
        is_recurring = values.get("is_recurring", False)

        if is_recurring and v is None:
            raise ValueError(
                "Frequência de recorrência é obrigatória para "
                "transações recorrentes"
            )

        if not is_recurring and v is not None:
            raise ValueError(
                "Frequência de recorrência deve ser None para "
                "transações não recorrentes"
            )

        return v

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: datetime) -> datetime:
        """Valida a data da transação."""
        from datetime import datetime, timedelta

        now = datetime.utcnow()
        # Permite até 30 dias no futuro para transações planejadas
        future_limit = now + timedelta(days=30)
        if v > future_limit:
            raise ValueError(
                "Data da transação não pode ser mais de 30 dias no futuro"
            )
        return v

    def update_amount(self, new_amount: Decimal) -> None:
        """Atualiza o valor da transação."""
        if new_amount <= 0:
            raise ValueError("Valor deve ser positivo")
        self.amount = new_amount
        self.updated_at = datetime.utcnow()

    def update_description(self, new_description: str) -> None:
        """Atualiza a descrição da transação."""
        new_description = new_description.strip()
        if not new_description:
            raise ValueError("Descrição não pode estar vazia")
        if len(new_description) > 500:
            raise ValueError("Descrição não pode ter mais de 500 caracteres")

        self.description = new_description
        self.updated_at = datetime.utcnow()

    def update_date(self, new_date: datetime) -> None:
        """Atualiza a data da transação."""
        now = datetime.utcnow()
        max_future_date = now + timedelta(days=30)
        if new_date > max_future_date:
            raise ValueError(
                "Data da transação não pode ser mais de 30 dias no futuro"
            )

        self.date = new_date
        self.updated_at = datetime.utcnow()

    def update_category(self, new_category_id: UUID) -> None:
        """Atualiza a categoria da transação."""
        self.category_id = new_category_id
        self.updated_at = datetime.utcnow()

    def update_account(self, new_account_id: UUID) -> None:
        """Atualiza a conta da transação."""
        self.account_id = new_account_id
        self.updated_at = datetime.utcnow()

    def make_recurring(self, frequency: RecurrenceType) -> None:
        """Torna a transação recorrente."""
        self.is_recurring = True
        self.recurrence_frequency = frequency
        self.updated_at = datetime.utcnow()

    def remove_recurrence(self) -> None:
        """Remove a recorrência da transação."""
        self.is_recurring = False
        self.recurrence_frequency = None
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Desativa a transação (soft delete)."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def duplicate(self, new_date: Optional[datetime] = None) -> "Transaction":
        """Cria uma cópia da transação com nova data."""
        if new_date is None:
            new_date = datetime.utcnow()

        return Transaction(
            user_id=self.user_id,
            account_id=self.account_id,
            category_id=self.category_id,
            type=self.type,
            amount=self.amount,
            description=self.description,
            date=new_date,
            is_recurring=self.is_recurring,
            recurrence_frequency=self.recurrence_frequency,
        )


class Category(BaseModel):
    """
    Entidade Category representando uma categoria de transação.

    Categorias podem ser do sistema (padrão) ou personalizadas do usuário.
    """

    id: UUID = Field(default_factory=uuid4)
    user_id: Optional[UUID] = None  # None para categorias do sistema
    name: str = Field(min_length=1, max_length=100)
    type: TransactionType
    is_system: bool = False
    parent_id: Optional[UUID] = None  # Para hierarquia futura
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Valida e limpa o nome da categoria."""
        v = v.strip()
        if not v:
            raise ValueError("Nome da categoria não pode estar vazio")
        return v

    def update_name(self, new_name: str) -> None:
        """Atualiza o nome da categoria."""
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("Nome da categoria não pode estar vazio")
        if len(new_name) > 100:
            raise ValueError(
                "Nome da categoria não pode ter mais de 100 caracteres"
            )

        self.name = new_name
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Desativa a categoria (soft delete)."""
        if self.is_system:
            raise ValueError("Categorias do sistema não podem ser desativadas")
        self.is_active = False
        self.updated_at = datetime.utcnow()

    @classmethod
    def create_system_category(
        cls, name: str, type: TransactionType
    ) -> "Category":
        """Cria uma categoria do sistema."""
        return cls(name=name, type=type, is_system=True)

    @classmethod
    def create_user_category(
        cls, user_id: UUID, name: str, type: TransactionType
    ) -> "Category":
        """Cria uma categoria personalizada do usuário."""
        return cls(user_id=user_id, name=name, type=type, is_system=False)


# Schemas Pydantic para requests e responses


class CreateTransactionRequest(BaseModel):
    """Schema para criação de transação."""

    account_id: UUID
    category_id: UUID
    type: TransactionType
    amount: Decimal = Field(gt=0)
    description: str = Field(min_length=1, max_length=500)
    date: datetime
    is_recurring: bool = False
    recurrence_frequency: Optional[RecurrenceType] = None


class UpdateTransactionRequest(BaseModel):
    """Schema para atualização de transação."""

    account_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    type: Optional[TransactionType] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    date: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurrence_frequency: Optional[RecurrenceType] = None


class TransactionResponse(BaseModel):
    """Schema para resposta de transação."""

    id: UUID
    account_id: UUID
    account_name: str
    category_id: UUID
    category_name: str
    type: TransactionType
    amount: Decimal
    description: str
    date: datetime
    is_recurring: bool
    recurrence_frequency: Optional[RecurrenceType]
    created_at: datetime
    updated_at: datetime


class TransactionSummaryResponse(BaseModel):
    """Schema para listagem resumida de transações."""

    id: UUID
    account_name: str
    category_name: str
    type: TransactionType
    amount: Decimal
    description: str
    date: datetime


class CreateCategoryRequest(BaseModel):
    """Schema para criação de categoria."""

    name: str = Field(min_length=1, max_length=100)
    type: TransactionType


class CategoryResponse(BaseModel):
    """Schema para resposta de categoria."""

    id: UUID
    name: str
    type: TransactionType
    is_system: bool
    created_at: datetime
