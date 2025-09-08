"""
Interfaces e ports para serviços de dashboard.

Define contratos para serviços de dashboard e analytics financeiros.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.core.domain.dashboard import (
    BalanceResponse,
    FinancialSummaryResponse,
    ExpensesByCategoryResponse,
    BalanceEvolutionResponse,
    RecentTransactionsResponse,
    IndicatorsResponse,
    PeriodFilter,
    BalanceEvolutionFilter,
    ExpensesCategoryFilter
)


class DashboardRepositoryPort(ABC):
    """Interface para repositório de dados de dashboard."""

    @abstractmethod
    async def get_consolidated_balance(self, user_id: UUID) -> BalanceResponse:
        """Obtém saldo consolidado de todas as contas do usuário."""
        pass

    @abstractmethod
    async def get_financial_summary(
        self, user_id: UUID, period_filter: PeriodFilter
    ) -> FinancialSummaryResponse:
        """Obtém resumo financeiro do período especificado."""
        pass

    @abstractmethod
    async def get_expenses_by_category(
        self, user_id: UUID, category_filter: ExpensesCategoryFilter
    ) -> ExpensesByCategoryResponse:
        """Obtém distribuição de despesas por categoria."""
        pass

    @abstractmethod
    async def get_balance_evolution(
        self, user_id: UUID, evolution_filter: BalanceEvolutionFilter
    ) -> BalanceEvolutionResponse:
        """Obtém evolução temporal dos saldos."""
        pass

    @abstractmethod
    async def get_recent_transactions(
        self, user_id: UUID, limit: int = 10
    ) -> RecentTransactionsResponse:
        """Obtém transações mais recentes do usuário."""
        pass


class FinancialAnalyticsServicePort(ABC):
    """Interface para serviço de analytics financeiros."""

    @abstractmethod
    async def calculate_financial_health_score(self, user_id: UUID) -> int:
        """Calcula score de saúde financeira (0-100)."""
        pass

    @abstractmethod
    async def generate_financial_indicators(self, user_id: UUID) -> List:
        """Gera indicadores financeiros personalizados."""
        pass

    @abstractmethod
    async def detect_alerts(self, user_id: UUID) -> List:
        """Detecta alertas baseados nos padrões financeiros."""
        pass

    @abstractmethod
    async def generate_suggestions(self, user_id: UUID) -> List:
        """Gera sugestões personalizadas baseadas no comportamento."""
        pass


class DashboardServicePort(ABC):
    """Interface para serviço principal de dashboard."""

    @abstractmethod
    async def get_dashboard_balance(self, user_id: UUID) -> BalanceResponse:
        """Obtém dados de saldo para dashboard."""
        pass

    @abstractmethod
    async def get_dashboard_summary(
        self, user_id: UUID, period_filter: Optional[PeriodFilter] = None
    ) -> FinancialSummaryResponse:
        """Obtém resumo financeiro para dashboard."""
        pass

    @abstractmethod
    async def get_dashboard_expenses_by_category(
        self, user_id: UUID, 
        category_filter: Optional[ExpensesCategoryFilter] = None
    ) -> ExpensesByCategoryResponse:
        """Obtém distribuição de despesas por categoria."""
        pass

    @abstractmethod
    async def get_dashboard_balance_evolution(
        self, user_id: UUID,
        evolution_filter: Optional[BalanceEvolutionFilter] = None
    ) -> BalanceEvolutionResponse:
        """Obtém evolução temporal dos saldos."""
        pass

    @abstractmethod
    async def get_dashboard_recent_transactions(
        self, user_id: UUID
    ) -> RecentTransactionsResponse:
        """Obtém transações recentes para dashboard."""
        pass

    @abstractmethod
    async def get_dashboard_indicators(
        self, user_id: UUID
    ) -> IndicatorsResponse:
        """Obtém indicadores, alertas e sugestões."""
        pass


class DashboardCachePort(ABC):
    """Interface para cache de dashboard."""

    @abstractmethod
    async def get_cached_balance(self, user_id: UUID) -> Optional[BalanceResponse]:
        """Obtém saldo em cache."""
        pass

    @abstractmethod
    async def cache_balance(
        self, user_id: UUID, data: BalanceResponse, ttl: int = 300
    ) -> None:
        """Armazena saldo em cache."""
        pass

    @abstractmethod
    async def get_cached_summary(
        self, user_id: UUID, cache_key: str
    ) -> Optional[FinancialSummaryResponse]:
        """Obtém resumo financeiro em cache."""
        pass

    @abstractmethod
    async def cache_summary(
        self, user_id: UUID, cache_key: str, 
        data: FinancialSummaryResponse, ttl: int = 300
    ) -> None:
        """Armazena resumo financeiro em cache."""
        pass

    @abstractmethod
    async def invalidate_user_cache(self, user_id: UUID) -> None:
        """Invalida todo cache de um usuário."""
        pass

    @abstractmethod
    async def invalidate_cache_pattern(self, pattern: str) -> None:
        """Invalida cache baseado em padrão."""
        pass
