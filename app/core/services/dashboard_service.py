"""
Implementação dos serviços de dashboard e analytics financeiros.

Contém a lógica de negócio para geração de métricas e análises financeiras.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict
from uuid import UUID
import calendar

from app.core.domain.dashboard import (
    BalanceResponse,
    FinancialSummaryResponse,
    ExpensesByCategoryResponse,
    BalanceEvolutionResponse,
    RecentTransactionsResponse,
    IndicatorsResponse,
    PeriodFilter,
    BalanceEvolutionFilter,
    ExpensesCategoryFilter,
    AccountSummary,
    CategoryExpense,
    BalancePoint,
    RecentTransaction,
    FinancialIndicator,
    Alert,
    Suggestion
)
from app.core.ports.dashboard import (
    DashboardServicePort,
    FinancialAnalyticsServicePort
)
from app.core.ports.account import AccountRepository
from app.core.ports.transaction import (
    TransactionRepository,
    CategoryRepository
)
from app.core.domain.transaction import TransactionType


class FinancialAnalyticsServiceImpl(FinancialAnalyticsServicePort):
    """Implementação do serviço de analytics financeiros."""

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository
    ):
        self.transaction_repository = transaction_repository
        self.account_repository = account_repository

    async def calculate_financial_health_score(self, user_id: UUID) -> int:
        """Calcula score de saúde financeira baseado em métricas."""
        score = 100
        
        # Pegar dados do último mês
        end_date = datetime.now()
        start_date = end_date.replace(day=1)
        
        try:
            # Buscar transações do período
            transactions = await self.transaction_repository.get_by_user_and_period(  # noqa: E501
                user_id, start_date, end_date
            )
            
            if not transactions:
                return 50  # Score neutro se não há transações
            
            # Calcular receitas e despesas
            total_income = sum(
                t.amount for t in transactions
                if t.type == TransactionType.INCOME
            )
            total_expenses = sum(
                t.amount for t in transactions
                if t.type == TransactionType.EXPENSE
            )
            
            # Análise 1: Taxa de poupança (30 pontos)
            if total_income > 0:
                savings_rate = (total_income - total_expenses) / total_income
                if savings_rate >= 0.2:  # 20% ou mais
                    pass  # Mantém pontos
                elif savings_rate >= 0.1:  # 10-19%
                    score -= 10
                elif savings_rate >= 0:  # 0-9%
                    score -= 20
                else:  # Gastando mais que ganha
                    score -= 30
            
            # Análise 2: Consistência de gastos (20 pontos)
            if len(transactions) >= 5:
                daily_expenses = {}
                for t in transactions:
                    if t.type == TransactionType.EXPENSE:
                        day = t.date.date()
                        daily_expenses[day] = (
                            daily_expenses.get(day, 0) + t.amount
                        )
                
                if daily_expenses:
                    expense_values = list(daily_expenses.values())
                    avg_expense = sum(expense_values) / len(expense_values)
                    variance = sum(
                        (x - avg_expense) ** 2 for x in expense_values
                    ) / len(expense_values)
                    
                    # Se variância muito alta, deduzir pontos
                    if variance > avg_expense:
                        score -= 20
                    elif variance > avg_expense * 0.5:
                        score -= 10
            
            # Análise 3: Diversificação de contas (10 pontos)
            user_accounts = await self.account_repository.get_by_user_id(  # noqa: E501
                user_id
            )
            if len(user_accounts) < 2:
                score -= 10
            
            return max(0, min(100, score))
            
        except Exception:
            return 50  # Score neutro em caso de erro

    async def generate_financial_indicators(self, user_id: UUID) -> List:
        """Gera indicadores financeiros personalizados."""
        indicators = []
        
        try:
            end_date = datetime.now()
            start_date = end_date.replace(day=1)
            
            transactions = await self.transaction_repository.get_by_user_and_period(
                user_id, start_date, end_date
            )
            
            if transactions:
                total_income = sum(
                    t.amount for t in transactions 
                    if t.type == TransactionType.INCOME
                )
                total_expenses = sum(
                    t.amount for t in transactions 
                    if t.type == TransactionType.EXPENSE
                )
                
                # Indicador 1: Taxa de poupança
                if total_income > 0:
                    savings_rate = (total_income - total_expenses) / total_income * 100
                    status = "good" if savings_rate >= 20 else "warning" if savings_rate >= 10 else "critical"
                    
                    indicators.append(FinancialIndicator(
                        name="Taxa de Poupança",
                        value=Decimal(str(round(savings_rate, 2))),
                        unit="%",
                        status=status,
                        description=f"Você está poupando {savings_rate:.1f}% da sua renda"
                    ))
                
                # Indicador 2: Gasto médio diário
                days_in_month = calendar.monthrange(end_date.year, end_date.month)[1]
                daily_avg = total_expenses / days_in_month
                
                indicators.append(FinancialIndicator(
                    name="Gasto Médio Diário",
                    value=Decimal(str(round(daily_avg, 2))),
                    unit="R$",
                    status="good",
                    description=f"Média de R$ {daily_avg:.2f} por dia"
                ))
            
        except Exception:
            pass
        
        return indicators

    async def detect_alerts(self, user_id: UUID) -> List:
        """Detecta alertas baseados nos padrões financeiros."""
        alerts = []
        
        try:
            # Verificar saldo baixo
            accounts = await self.account_repository.get_by_user_id(user_id)
            for account in accounts:
                if account.balance < Decimal("100"):
                    alerts.append(Alert(
                        id=f"low_balance_{account.id}",
                        type="low_balance",
                        severity="medium",
                        title="Saldo Baixo",
                        message=f"Conta {account.name} com saldo baixo: R$ {account.balance}",
                        created_at=datetime.now()
                    ))
        
        except Exception:
            pass
        
        return alerts

    async def generate_suggestions(self, user_id: UUID) -> List:
        """Gera sugestões personalizadas."""
        suggestions = []
        
        try:
            end_date = datetime.now()
            start_date = end_date.replace(day=1)
            
            transactions = await self.transaction_repository.get_by_user_and_period(
                user_id, start_date, end_date
            )
            
            if transactions:
                expense_transactions = [
                    t for t in transactions 
                    if t.type == TransactionType.EXPENSE
                ]
                
                if len(expense_transactions) > 0:
                    avg_expense = sum(t.amount for t in expense_transactions) / len(expense_transactions)
                    
                    if avg_expense > Decimal("200"):
                        suggestions.append(Suggestion(
                            id="reduce_expenses",
                            category="spending",
                            title="Revisar Gastos",
                            description="Considere revisar suas despesas maiores para otimizar seu orçamento",
                            potential_impact="Economia de até 15% nos gastos mensais"
                        ))
            
        except Exception:
            pass
        
        return suggestions


class DashboardServiceImpl(DashboardServicePort):
    """Implementação do serviço principal de dashboard."""

    def __init__(
        self,
        account_repository: AccountRepository,
        transaction_repository: TransactionRepository,
        category_repository: CategoryRepository,
        analytics_service: FinancialAnalyticsServiceImpl
    ):
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository
        self.category_repository = category_repository
        self.analytics_service = analytics_service

    async def get_dashboard_balance(self, user_id: UUID) -> BalanceResponse:
        """Obtém dados de saldo consolidado."""
        accounts = await self.account_repository.get_by_user_id(user_id)
        
        total_balance = Decimal("0")
        balance_by_type: Dict[str, Decimal] = {}
        account_summaries = []
        
        for account in accounts:
            if account.is_active:
                total_balance += account.balance
                
                account_type = account.type.value
                balance_by_type[account_type] = balance_by_type.get(account_type, Decimal("0")) + account.balance
                
                account_summaries.append(AccountSummary(
                    id=account.id,
                    name=account.name,
                    type=account_type,
                    balance=account.balance,
                    is_primary=account.is_primary
                ))
        
        return BalanceResponse(
            total_balance=total_balance,
            balance_by_type=balance_by_type,
            accounts=account_summaries,
            last_updated=datetime.now()
        )

    async def get_dashboard_summary(
        self, user_id: UUID, period_filter: Optional[PeriodFilter] = None
    ) -> FinancialSummaryResponse:
        """Obtém resumo financeiro do período."""
        if not period_filter:
            # Período padrão: mês atual
            now = datetime.now()
            period_filter = PeriodFilter(
                start_date=now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                end_date=now
            )
        
        transactions = await self.transaction_repository.get_by_user_and_period(
            user_id, period_filter.start_date, period_filter.end_date
        )
        
        # Calcular métricas básicas
        income_transactions = [t for t in transactions if t.type == TransactionType.INCOME]
        expense_transactions = [t for t in transactions if t.type == TransactionType.EXPENSE]
        
        total_income = sum(t.amount for t in income_transactions)
        total_expenses = sum(t.amount for t in expense_transactions)
        net_balance = total_income - total_expenses
        
        # Métricas adicionais
        highest_income = max((t.amount for t in income_transactions), default=Decimal("0"))
        highest_expense = max((t.amount for t in expense_transactions), default=Decimal("0"))
        
        # Calcular médias diárias
        period_days = (period_filter.end_date - period_filter.start_date).days + 1
        daily_avg_income = total_income / period_days if period_days > 0 else Decimal("0")
        daily_avg_expenses = total_expenses / period_days if period_days > 0 else Decimal("0")
        
        return FinancialSummaryResponse(
            period_start=period_filter.start_date,
            period_end=period_filter.end_date,
            total_income=total_income,
            total_expenses=total_expenses,
            net_balance=net_balance,
            highest_income=highest_income,
            highest_expense=highest_expense,
            daily_average_income=daily_avg_income,
            daily_average_expenses=daily_avg_expenses,
            total_transactions=len(transactions),
            income_transactions=len(income_transactions),
            expense_transactions=len(expense_transactions)
        )

    async def get_dashboard_expenses_by_category(
        self, user_id: UUID, 
        category_filter: Optional[ExpensesCategoryFilter] = None
    ) -> ExpensesByCategoryResponse:
        """Obtém distribuição de despesas por categoria."""
        if not category_filter:
            now = datetime.now()
            category_filter = ExpensesCategoryFilter(
                start_date=now.replace(day=1),
                end_date=now,
                limit=10,
                include_others=True
            )
        
        transactions = await self.transaction_repository.get_by_user_and_period(
            user_id, category_filter.start_date, category_filter.end_date
        )
        
        expense_transactions = [t for t in transactions if t.type == TransactionType.EXPENSE]
        total_expenses = sum(t.amount for t in expense_transactions)
        
        # Agrupar por categoria
        category_expenses: Dict[UUID, Decimal] = {}
        category_counts: Dict[UUID, int] = {}
        
        for transaction in expense_transactions:
            cat_id = transaction.category_id
            category_expenses[cat_id] = category_expenses.get(cat_id, Decimal("0")) + transaction.amount
            category_counts[cat_id] = category_counts.get(cat_id, 0) + 1
        
        # Buscar nomes das categorias
        categories = []
        others_amount = Decimal("0")
        
        sorted_categories = sorted(
            category_expenses.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for i, (cat_id, amount) in enumerate(sorted_categories):
            if i < category_filter.limit:
                try:
                    category = await self.category_repository.get_by_id(cat_id, user_id)
                    if category:
                        percentage = (amount / total_expenses * 100) if total_expenses > 0 else Decimal("0")
                        categories.append(CategoryExpense(
                            category_id=cat_id,
                            category_name=category.name,
                            total_amount=amount,
                            percentage=percentage,
                            transaction_count=category_counts[cat_id]
                        ))
                except Exception:
                    others_amount += amount
            else:
                others_amount += amount
        
        others_percentage = (others_amount / total_expenses * 100) if total_expenses > 0 else Decimal("0")
        
        return ExpensesByCategoryResponse(
            period_start=category_filter.start_date,
            period_end=category_filter.end_date,
            total_expenses=total_expenses,
            categories=categories,
            others_amount=others_amount,
            others_percentage=others_percentage
        )

    async def get_dashboard_balance_evolution(
        self, user_id: UUID,
        evolution_filter: Optional[BalanceEvolutionFilter] = None
    ) -> BalanceEvolutionResponse:
        """Obtém evolução temporal dos saldos."""
        if not evolution_filter:
            now = datetime.now()
            evolution_filter = BalanceEvolutionFilter(
                end_date=now,
                start_date=now - timedelta(days=365),
                granularity="monthly",
                months_back=12
            )
        
        # Para simplificar, vamos calcular pontos mensais
        data_points = []
        current_date = evolution_filter.start_date
        
        # Obter saldo inicial das contas
        accounts = await self.account_repository.get_by_user_id(user_id)
        initial_balance = sum(account.balance for account in accounts)
        
        # Para demo, criar alguns pontos de dados básicos
        for i in range(12):
            point_date = current_date + timedelta(days=30 * i)
            # Simulação simples - em produção seria baseado em transações históricas
            balance_variation = Decimal(str(i * 100))  # Crescimento fictício
            
            data_points.append(BalancePoint(
                date=point_date,
                balance=initial_balance + balance_variation,
                cumulative_income=Decimal(str(i * 2000)),
                cumulative_expenses=Decimal(str(i * 1500))
            ))
        
        # Calcular tendência
        if len(data_points) >= 2:
            start_balance = data_points[0].balance
            end_balance = data_points[-1].balance
            trend_percentage = ((end_balance - start_balance) / start_balance * 100) if start_balance > 0 else Decimal("0")
            
            if trend_percentage > 5:
                trend = "growing"
            elif trend_percentage < -5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
            trend_percentage = Decimal("0")
        
        return BalanceEvolutionResponse(
            period_start=evolution_filter.start_date,
            period_end=evolution_filter.end_date,
            granularity=evolution_filter.granularity,
            data_points=data_points,
            trend=trend,
            trend_percentage=trend_percentage
        )

    async def get_dashboard_recent_transactions(
        self, user_id: UUID
    ) -> RecentTransactionsResponse:
        """Obtém transações recentes."""
        transactions = await self.transaction_repository.get_recent_by_user(user_id, limit=10)
        
        recent_transactions = []
        total_amount = Decimal("0")
        
        for transaction in transactions:
            # Buscar dados da conta e categoria
            try:
                account = await self.account_repository.get_by_id(transaction.account_id, user_id)
                category = await self.category_repository.get_by_id(transaction.category_id, user_id)
                
                if account and category:
                    recent_transactions.append(RecentTransaction(
                        id=transaction.id,
                        date=transaction.date,
                        description=transaction.description,
                        amount=transaction.amount,
                        type=transaction.type.value,
                        account_name=account.name,
                        category_name=category.name
                    ))
                    total_amount += transaction.amount
            except Exception:
                continue
        
        return RecentTransactionsResponse(
            transactions=recent_transactions,
            total_recent_amount=total_amount
        )

    async def get_dashboard_indicators(
        self, user_id: UUID
    ) -> IndicatorsResponse:
        """Obtém indicadores, alertas e sugestões."""
        # Calcular score de saúde financeira
        health_score = await self.analytics_service.calculate_financial_health_score(user_id)
        
        # Gerar indicadores
        indicators = await self.analytics_service.generate_financial_indicators(user_id)
        
        # Detectar alertas
        alerts = await self.analytics_service.detect_alerts(user_id)
        
        # Gerar sugestões
        suggestions = await self.analytics_service.generate_suggestions(user_id)
        
        return IndicatorsResponse(
            financial_health_score=health_score,
            indicators=indicators,
            alerts=alerts,
            suggestions=suggestions
        )
