"""
Interfaces e ports para serviços de dashboard.

Define contratos para serviços de dashboard e analytics financeiros.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.core.domain.dashboard import (
    BalanceEvolutionFilter,
    BalanceEvolutionResponse,
    BalanceResponse,
    ExpensesByCategoryResponse,
    ExpensesCategoryFilter,
    FinancialSummaryResponse,
    IndicatorsResponse,
    PeriodFilter,
    RecentTransactionsResponse,
)


class DashboardRepositoryPort(ABC):
    """Interface para repositório de dados de dashboard."""

    @abstractmethod
    async def get_consolidated_balance(self, user_id: UUID) -> BalanceResponse:
        """Obtém saldo consolidado de todas as contas do usuário."""

    @abstractmethod
    async def get_financial_summary(
        self, user_id: UUID, period_filter: PeriodFilter
    ) -> FinancialSummaryResponse:
        """Obtém resumo financeiro do período especificado."""

    @abstractmethod
    async def get_expenses_by_category(
        self, user_id: UUID, category_filter: ExpensesCategoryFilter
    ) -> ExpensesByCategoryResponse:
        """Obtém distribuição de despesas por categoria."""

    @abstractmethod
    async def get_balance_evolution(
        self, user_id: UUID, evolution_filter: BalanceEvolutionFilter
    ) -> BalanceEvolutionResponse:
        """Obtém evolução temporal dos saldos."""

    @abstractmethod
    async def get_recent_transactions(
        self, user_id: UUID, limit: int = 10
    ) -> RecentTransactionsResponse:
        """Obtém transações mais recentes do usuário."""


class FinancialAnalyticsServicePort(ABC):
    """Interface para serviço de analytics financeiros."""

    @abstractmethod
    async def calculate_financial_health_score(self, user_id: UUID) -> int:
        """Calcula score de saúde financeira (0-100)."""

    @abstractmethod
    async def generate_financial_indicators(self, user_id: UUID) -> List:
        """Gera indicadores financeiros personalizados."""

    @abstractmethod
    async def detect_alerts(self, user_id: UUID) -> List:
        """Detecta alertas baseados nos padrões financeiros."""

    @abstractmethod
    async def generate_suggestions(self, user_id: UUID) -> List:
        """Gera sugestões personalizadas baseadas no comportamento."""


class DashboardServicePort(ABC):
    """Interface para serviço principal de dashboard."""

    @abstractmethod
    async def get_dashboard_balance(self, user_id: UUID) -> BalanceResponse:
        """Obtém dados de saldo para dashboard."""

    @abstractmethod
    async def get_dashboard_summary(
        self, user_id: UUID, period_filter: Optional[PeriodFilter] = None
    ) -> FinancialSummaryResponse:
        """Obtém resumo financeiro para dashboard."""

    @abstractmethod
    async def get_dashboard_expenses_by_category(
        self,
        user_id: UUID,
        category_filter: Optional[ExpensesCategoryFilter] = None,
    ) -> ExpensesByCategoryResponse:
        """Obtém distribuição de despesas por categoria."""

    @abstractmethod
    async def get_dashboard_balance_evolution(
        self,
        user_id: UUID,
        evolution_filter: Optional[BalanceEvolutionFilter] = None,
    ) -> BalanceEvolutionResponse:
        """Obtém evolução temporal dos saldos."""

    @abstractmethod
    async def get_dashboard_recent_transactions(
        self, user_id: UUID
    ) -> RecentTransactionsResponse:
        """Obtém transações recentes para dashboard."""

    @abstractmethod
    async def get_dashboard_indicators(
        self, user_id: UUID
    ) -> IndicatorsResponse:
        """Obtém indicadores, alertas e sugestões."""


class DashboardCachePort(ABC):
    """Interface para cache de dashboard."""

    @abstractmethod
    async def get_cached_balance(
        self, user_id: UUID
    ) -> Optional[BalanceResponse]:
        """Obtém saldo em cache."""

    @abstractmethod
    async def cache_balance(
        self, user_id: UUID, data: BalanceResponse, ttl: int = 300
    ) -> None:
        """Armazena saldo em cache."""

    @abstractmethod
    async def get_cached_summary(
        self, user_id: UUID, cache_key: str
    ) -> Optional[FinancialSummaryResponse]:
        """Obtém resumo financeiro em cache."""

    @abstractmethod
    async def cache_summary(
        self,
        user_id: UUID,
        cache_key: str,
        data: FinancialSummaryResponse,
        ttl: int = 300,
    ) -> None:
        """Armazena resumo financeiro em cache."""

    @abstractmethod
    async def invalidate_user_cache(self, user_id: UUID) -> None:
        """Invalida todo cache de um usuário."""

    @abstractmethod
    async def invalidate_cache_pattern(self, pattern: str) -> None:
        """Invalida cache baseado em padrão."""
