"""
DTOs e schemas para respostas de dashboard.

Contém modelos de dados específicos para endpoints de dashboard,
otimizados para agregações e visualizações financeiras.
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict
from uuid import UUID

from pydantic import BaseModel, Field


class AccountSummary(BaseModel):
    """Resumo de conta para dashboard."""
    id: UUID
    name: str
    type: str
    balance: Decimal
    is_primary: bool


class BalanceResponse(BaseModel):
    """Resposta para saldo consolidado."""
    total_balance: Decimal = Field(..., description="Saldo total de todas as contas")
    balance_by_type: Dict[str, Decimal] = Field(
        ..., description="Saldo agrupado por tipo de conta"
    )
    accounts: List[AccountSummary] = Field(
        ..., description="Lista resumida de contas"
    )
    last_updated: datetime = Field(..., description="Última atualização dos dados")


class PeriodComparison(BaseModel):
    """Comparação entre períodos."""
    current_value: Decimal
    previous_value: Decimal
    variation_amount: Decimal
    variation_percentage: Decimal


class FinancialSummaryResponse(BaseModel):
    """Resumo financeiro do período."""
    period_start: datetime
    period_end: datetime
    total_income: Decimal = Field(..., description="Total de receitas no período")
    total_expenses: Decimal = Field(..., description="Total de despesas no período")
    net_balance: Decimal = Field(..., description="Saldo líquido (receitas - despesas)")
    
    # Comparações com período anterior
    income_comparison: Optional[PeriodComparison] = None
    expenses_comparison: Optional[PeriodComparison] = None
    
    # Métricas adicionais
    highest_income: Decimal = Field(..., description="Maior receita individual")
    highest_expense: Decimal = Field(..., description="Maior despesa individual")
    daily_average_income: Decimal = Field(..., description="Média diária de receitas")
    daily_average_expenses: Decimal = Field(..., description="Média diária de despesas")
    
    # Contadores
    total_transactions: int = Field(..., description="Total de transações no período")
    income_transactions: int = Field(..., description="Número de receitas")
    expense_transactions: int = Field(..., description="Número de despesas")


class CategoryExpense(BaseModel):
    """Despesa por categoria."""
    category_id: UUID
    category_name: str
    total_amount: Decimal
    percentage: Decimal
    transaction_count: int


class ExpensesByCategoryResponse(BaseModel):
    """Resposta para distribuição de despesas por categoria."""
    period_start: datetime
    period_end: datetime
    total_expenses: Decimal
    categories: List[CategoryExpense] = Field(
        ..., description="Despesas agrupadas por categoria"
    )
    others_amount: Decimal = Field(
        ..., description="Valor agrupado em 'Outros'"
    )
    others_percentage: Decimal = Field(
        ..., description="Percentual de 'Outros'"
    )


class BalancePoint(BaseModel):
    """Ponto de saldo para evolução temporal."""
    date: datetime
    balance: Decimal
    cumulative_income: Decimal
    cumulative_expenses: Decimal


class BalanceEvolutionResponse(BaseModel):
    """Resposta para evolução temporal dos saldos."""
    period_start: datetime
    period_end: datetime
    granularity: str = Field(..., description="daily ou monthly")
    data_points: List[BalancePoint] = Field(
        ..., description="Pontos de dados para gráfico"
    )
    trend: str = Field(
        ..., description="growing, declining, stable"
    )
    trend_percentage: Decimal = Field(
        ..., description="Percentual de crescimento/declínio"
    )


class RecentTransaction(BaseModel):
    """Transação recente para dashboard."""
    id: UUID
    date: datetime
    description: str
    amount: Decimal
    type: str
    account_name: str
    category_name: str


class RecentTransactionsResponse(BaseModel):
    """Resposta para transações recentes."""
    transactions: List[RecentTransaction] = Field(
        max_items=10, description="Últimas 10 transações"
    )
    total_recent_amount: Decimal = Field(
        ..., description="Soma das transações recentes"
    )


class FinancialIndicator(BaseModel):
    """Indicador financeiro."""
    name: str
    value: Decimal
    unit: str = Field(..., description="%, R$, dias, etc")
    status: str = Field(..., description="good, warning, critical")
    description: str


class Alert(BaseModel):
    """Alerta financeiro."""
    id: str
    type: str = Field(..., description="budget, low_balance, unusual_spending")
    severity: str = Field(..., description="low, medium, high")
    title: str
    message: str
    created_at: datetime


class Suggestion(BaseModel):
    """Sugestão personalizada."""
    id: str
    category: str = Field(..., description="saving, spending, budget")
    title: str
    description: str
    potential_impact: str


class IndicatorsResponse(BaseModel):
    """Resposta para indicadores e alertas."""
    financial_health_score: int = Field(
        ..., ge=0, le=100, description="Score de saúde financeira"
    )
    indicators: List[FinancialIndicator] = Field(
        ..., description="Indicadores principais"
    )
    alerts: List[Alert] = Field(
        ..., description="Alertas ativos"
    )
    suggestions: List[Suggestion] = Field(
        ..., description="Sugestões personalizadas"
    )


# Request schemas para filtros de período
class PeriodFilter(BaseModel):
    """Filtro de período para consultas de dashboard."""
    start_date: Optional[datetime] = Field(
        None, description="Data de início (padrão: início do mês atual)"
    )
    end_date: Optional[datetime] = Field(
        None, description="Data de fim (padrão: fim do mês atual)"
    )


class BalanceEvolutionFilter(PeriodFilter):
    """Filtro para evolução de saldos."""
    granularity: str = Field(
        "monthly", description="daily ou monthly"
    )
    months_back: int = Field(
        12, ge=1, le=24, description="Meses para trás (padrão: 12)"
    )


class ExpensesCategoryFilter(PeriodFilter):
    """Filtro para despesas por categoria."""
    limit: int = Field(
        10, ge=5, le=20, description="Limite de categorias (padrão: 10)"
    )
    include_others: bool = Field(
        True, description="Incluir categoria 'Outros'"
    )
