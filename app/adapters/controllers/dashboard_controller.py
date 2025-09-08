"""
Controladores REST para os endpoints de dashboard.

Contém os endpoints para métricas, analytics e visualizações do dashboard.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

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
from app.core.ports.dashboard import DashboardServicePort
from app.core.services.dashboard_service import DashboardServiceImpl
from app.adapters.outbound.memory_repositories import (
    InMemoryAccountRepository,
    InMemoryTransactionRepository,
    InMemoryCategoryRepository
)
from app.core.services.dashboard_service import FinancialAnalyticsServiceImpl
from app.adapters.inbound.auth_middleware import get_current_user
from app.core.domain.user import UserResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_current_user_id(
    current_user: UserResponse = Depends(get_current_user)
) -> UUID:
    """Extrai o ID do usuário atual."""
    return UUID(current_user.id)


def get_dashboard_service() -> DashboardServicePort:
    """Dependency para injeção do serviço de dashboard."""
    account_repo = InMemoryAccountRepository()
    transaction_repo = InMemoryTransactionRepository()
    category_repo = InMemoryCategoryRepository()
    analytics_service = FinancialAnalyticsServiceImpl(
        transaction_repo, account_repo
    )
    
    return DashboardServiceImpl(
        account_repo,
        transaction_repo,
        category_repo,
        analytics_service
    )


@router.get("/balance", response_model=BalanceResponse)
async def get_dashboard_balance(
    user_id: UUID = Depends(get_current_user_id),
    dashboard_service: DashboardServicePort = Depends(get_dashboard_service)
):
    """
    Obtém o saldo consolidado do usuário.
    
    Retorna informações sobre:
    - Saldo total de todas as contas
    - Distribuição por tipo de conta
    - Lista de contas com seus saldos
    """
    try:
        return await dashboard_service.get_dashboard_balance(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter saldo do dashboard: {str(e)}"
        )


@router.get("/summary", response_model=FinancialSummaryResponse)
async def get_dashboard_summary(
    start_date: Optional[datetime] = Query(
        None, description="Data inicial do período (ISO 8601)"
    ),
    end_date: Optional[datetime] = Query(
        None, description="Data final do período (ISO 8601)"
    ),
    user_id: UUID = Depends(get_current_user_id),
    dashboard_service: DashboardServicePort = Depends(get_dashboard_service)
):
    """
    Obtém o resumo financeiro do período especificado.
    
    Se as datas não forem fornecidas, retorna dados do mês atual.
    
    Retorna informações sobre:
    - Total de receitas e despesas
    - Saldo líquido do período
    - Maior receita e maior despesa
    - Médias diárias
    - Contadores de transações
    """
    try:
        period_filter = None
        if start_date and end_date:
            period_filter = PeriodFilter(
                start_date=start_date,
                end_date=end_date
            )
        
        return await dashboard_service.get_dashboard_summary(
            user_id, period_filter
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter resumo do dashboard: {str(e)}"
        )


@router.get("/expenses-by-category", response_model=ExpensesByCategoryResponse)
async def get_dashboard_expenses_by_category(
    start_date: Optional[datetime] = Query(
        None, description="Data inicial do período (ISO 8601)"
    ),
    end_date: Optional[datetime] = Query(
        None, description="Data final do período (ISO 8601)"
    ),
    limit: int = Query(
        10, description="Número máximo de categorias a retornar", ge=1, le=50
    ),
    include_others: bool = Query(
        True, description="Incluir categoria 'Outros' para o restante"
    ),
    user_id: UUID = Depends(get_current_user_id),
    dashboard_service: DashboardServicePort = Depends(get_dashboard_service)
):
    """
    Obtém a distribuição de despesas por categoria no período.
    
    Se as datas não forem fornecidas, retorna dados do mês atual.
    
    Retorna:
    - Lista das principais categorias com valores e percentuais
    - Total de despesas do período
    - Categoria "Outros" consolidando o restante (se habilitada)
    """
    try:
        category_filter = None
        if start_date and end_date:
            category_filter = ExpensesCategoryFilter(
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                include_others=include_others
            )
        else:
            # Período padrão: mês atual
            now = datetime.now()
            category_filter = ExpensesCategoryFilter(
                start_date=now.replace(day=1),
                end_date=now,
                limit=limit,
                include_others=include_others
            )
        
        return await dashboard_service.get_dashboard_expenses_by_category(
            user_id, category_filter
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter despesas por categoria: {str(e)}"
        )


@router.get("/balance-evolution", response_model=BalanceEvolutionResponse)
async def get_dashboard_balance_evolution(
    start_date: Optional[datetime] = Query(
        None, description="Data inicial do período (ISO 8601)"
    ),
    end_date: Optional[datetime] = Query(
        None, description="Data final do período (ISO 8601)"
    ),
    granularity: str = Query(
        "monthly",
        description="Granularidade dos dados",
        regex="^(daily|weekly|monthly)$"
    ),
    months_back: int = Query(
        12, description="Meses para trás a partir da data final", ge=1, le=36
    ),
    user_id: UUID = Depends(get_current_user_id),
    dashboard_service: DashboardServicePort = Depends(get_dashboard_service)
):
    """
    Obtém a evolução temporal dos saldos.
    
    Se as datas não forem fornecidas, retorna dados dos últimos 12 meses.
    
    Retorna:
    - Série temporal de pontos com saldo, receitas e despesas acumuladas
    - Análise de tendência (crescente, estável, decrescente)
    - Percentual de crescimento/declínio
    """
    try:
        evolution_filter = None
        if start_date and end_date:
            evolution_filter = BalanceEvolutionFilter(
                start_date=start_date,
                end_date=end_date,
                granularity=granularity,
                months_back=months_back
            )
        else:
            # Período padrão: últimos X meses
            now = datetime.now()
            evolution_filter = BalanceEvolutionFilter(
                end_date=now,
                start_date=now - timedelta(days=30 * months_back),
                granularity=granularity,
                months_back=months_back
            )
        
        return await dashboard_service.get_dashboard_balance_evolution(
            user_id, evolution_filter
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter evolução de saldos: {str(e)}"
        )


@router.get("/recent-transactions", response_model=RecentTransactionsResponse)
async def get_dashboard_recent_transactions(
    user_id: UUID = Depends(get_current_user_id),
    dashboard_service: DashboardServicePort = Depends(get_dashboard_service)
):
    """
    Obtém as transações mais recentes do usuário.
    
    Retorna:
    - Lista das 10 transações mais recentes
    - Informações básicas: data, descrição, valor, tipo, conta e categoria
    - Total dos valores das transações recentes
    """
    try:
        return await dashboard_service.get_dashboard_recent_transactions(  # noqa: E501
            user_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter transações recentes: {str(e)}"
        )


@router.get("/indicators", response_model=IndicatorsResponse)
async def get_dashboard_indicators(
    user_id: UUID = Depends(get_current_user_id),
    dashboard_service: DashboardServicePort = Depends(get_dashboard_service)
):
    """
    Obtém indicadores, alertas e sugestões personalizadas.
    
    Retorna:
    - Score de saúde financeira (0-100)
    - Indicadores financeiros chave
    - Alertas baseados em padrões identificados
    - Sugestões personalizadas para melhoria
    """
    try:
        return await dashboard_service.get_dashboard_indicators(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter indicadores: {str(e)}"
        )
