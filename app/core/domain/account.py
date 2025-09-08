"""
Modelos de domínio para Conta Financeira.

Este módulo contém as entidades e value objects relacionados à gestão
de contas financeiras no sistema.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class AccountType(str, Enum):
    """Tipos de conta financeira disponíveis."""
    
    CHECKING = "checking"  # Conta corrente
    SAVINGS = "savings"    # Poupança
    CREDIT_CARD = "credit_card"  # Cartão de crédito
    INVESTMENT = "investment"    # Investimento


class Account(BaseModel):
    """
    Entidade Account representando uma conta financeira.
    
    Contém as regras de negócio para gestão de contas financeiras,
    incluindo validações específicas por tipo de conta.
    """
    
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    name: str = Field(min_length=1, max_length=100)
    type: AccountType
    balance: Decimal = Field(default=Decimal("0.00"))
    is_primary: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    @field_validator("balance")
    @classmethod
    def validate_balance(cls, v: Decimal) -> Decimal:
        """
        Valida saldo básico.
        
        Validações específicas por tipo de conta serão feitas no service.
        """
        return v
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Valida e limpa o nome da conta."""
        name = v.strip()
        if not name:
            raise ValueError("Nome da conta não pode estar vazio")
        return name
    
    def is_credit_card(self) -> bool:
        """Verifica se a conta é do tipo cartão de crédito."""
        return self.type == AccountType.CREDIT_CARD
    
    def can_have_negative_balance(self) -> bool:
        """Verifica se a conta pode ter saldo negativo."""
        return self.is_credit_card()
    
    def set_as_primary(self) -> None:
        """Define esta conta como principal."""
        self.is_primary = True
        self.updated_at = datetime.utcnow()
    
    def remove_primary_status(self) -> None:
        """Remove o status de conta principal."""
        self.is_primary = False
        self.updated_at = datetime.utcnow()
    
    def update_balance(self, new_balance: Decimal) -> None:
        """
        Atualiza o saldo da conta com validações.
        
        Args:
            new_balance: Novo saldo da conta
            
        Raises:
            ValueError: Se saldo negativo não for permitido para o tipo
        """
        if new_balance < 0 and not self.can_have_negative_balance():
            raise ValueError(
                f"Saldo negativo não permitido para conta do tipo {self.type}"
            )
        
        self.balance = new_balance
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Desativa a conta (soft delete)."""
        self.is_active = False
        self.is_primary = False  # Conta inativa não pode ser principal
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Reativa a conta."""
        self.is_active = True
        self.updated_at = datetime.utcnow()


class CreateAccountRequest(BaseModel):
    """Schema para criação de nova conta."""
    
    name: str = Field(min_length=1, max_length=100)
    type: AccountType
    balance: Decimal = Field(default=Decimal("0.00"))
    is_primary: bool = Field(default=False)
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Valida e limpa o nome da conta."""
        name = v.strip()
        if not name:
            raise ValueError("Nome da conta não pode estar vazio")
        return name


class UpdateAccountRequest(BaseModel):
    """Schema para atualização de conta existente."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[AccountType] = None
    balance: Optional[Decimal] = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Valida e limpa o nome da conta se fornecido."""
        if v is not None:
            name = v.strip()
            if not name:
                raise ValueError("Nome da conta não pode estar vazio")
            return name
        return v


class AccountResponse(BaseModel):
    """Schema para resposta de conta."""
    
    id: UUID
    name: str
    type: AccountType
    balance: Decimal
    is_primary: bool
    created_at: datetime
    updated_at: datetime
    is_active: bool


class AccountSummaryResponse(BaseModel):
    """Schema para resposta resumida de conta na listagem."""
    
    id: UUID
    name: str
    type: AccountType
    balance: Decimal
    is_primary: bool
