"""
Testes unitários para os serviços de dashboard.

Testa a lógica de negócio dos serviços de analytics e dashboard.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from app.core.services.dashboard_service import (
    DashboardServiceImpl,
    FinancialAnalyticsServiceImpl
)
from app.core.domain.account import Account, AccountType
from app.core.domain.transaction import Transaction, TransactionType, Category
from app.core.domain.dashboard import (
    PeriodFilter,
    BalanceEvolutionFilter,
    ExpensesCategoryFilter
)
from app.adapters.outbound.memory_repositories import (
    InMemoryAccountRepository,
    InMemoryTransactionRepository,
    InMemoryCategoryRepository
)


@pytest.fixture
def user_id():
    """Fixture que retorna um ID de usuário para testes."""
    return uuid4()


@pytest.fixture
def account_repository():
    """Fixture do repositório de contas em memória."""
    return InMemoryAccountRepository()


@pytest.fixture
def transaction_repository():
    """Fixture do repositório de transações em memória."""
    return InMemoryTransactionRepository()


@pytest.fixture
def category_repository():
    """Fixture do repositório de categorias em memória."""
    return InMemoryCategoryRepository()


@pytest.fixture
def analytics_service(account_repository, transaction_repository):
    """Fixture do serviço de analytics."""
    return FinancialAnalyticsServiceImpl(
        transaction_repository, account_repository
    )


@pytest.fixture
def dashboard_service(
    account_repository,
    transaction_repository,
    category_repository,
    analytics_service
):
    """Fixture do serviço de dashboard."""
    return DashboardServiceImpl(
        account_repository,
        transaction_repository,
        category_repository,
        analytics_service
    )


@pytest.fixture
async def sample_accounts(account_repository, user_id):
    """Fixture que cria contas de exemplo."""
    account1 = Account(
        id=uuid4(),
        user_id=user_id,
        name="Conta Corrente",
        type=AccountType.CHECKING,
        balance=Decimal("1500.00"),
        is_active=True,
        is_primary=True
    )
    
    account2 = Account(
        id=uuid4(),
        user_id=user_id,
        name="Poupança",
        type=AccountType.SAVINGS,
        balance=Decimal("5000.00"),
        is_active=True,
        is_primary=False
    )
    
    await account_repository.create(account1)
    await account_repository.create(account2)
    
    return [account1, account2]


@pytest.fixture
async def sample_categories(category_repository, user_id):
    """Fixture que cria categorias de exemplo."""
    category1 = Category(
        id=uuid4(),
        user_id=user_id,
        name="Alimentação",
        type=TransactionType.EXPENSE
    )
    
    category2 = Category(
        id=uuid4(),
        user_id=user_id,
        name="Transporte",
        type=TransactionType.EXPENSE
    )
    
    category3 = Category(
        id=uuid4(),
        user_id=user_id,
        name="Salário",
        type=TransactionType.INCOME
    )
    
    await category_repository.create(category1)
    await category_repository.create(category2)
    await category_repository.create(category3)
    
    return [category1, category2, category3]


@pytest.fixture
async def sample_transactions(
    transaction_repository,
    user_id,
    sample_accounts,
    sample_categories
):
    """Fixture que cria transações de exemplo."""
    account1, account2 = sample_accounts
    cat_food, cat_transport, cat_salary = sample_categories
    
    now = datetime.now()
    
    transactions = [
        # Receitas
        Transaction(
            id=uuid4(),
            user_id=user_id,
            account_id=account1.id,
            category_id=cat_salary.id,
            type=TransactionType.INCOME,
            amount=Decimal("3000.00"),
            description="Salário",
            date=now - timedelta(days=5)
        ),
        
        # Despesas
        Transaction(
            id=uuid4(),
            user_id=user_id,
            account_id=account1.id,
            category_id=cat_food.id,
            type=TransactionType.EXPENSE,
            amount=Decimal("150.00"),
            description="Supermercado",
            date=now - timedelta(days=3)
        ),
        
        Transaction(
            id=uuid4(),
            user_id=user_id,
            account_id=account1.id,
            category_id=cat_transport.id,
            type=TransactionType.EXPENSE,
            amount=Decimal("80.00"),
            description="Combustível",
            date=now - timedelta(days=2)
        ),
        
        Transaction(
            id=uuid4(),
            user_id=user_id,
            account_id=account2.id,
            category_id=cat_food.id,
            type=TransactionType.EXPENSE,
            amount=Decimal("200.00"),
            description="Restaurante",
            date=now - timedelta(days=1)
        )
    ]
    
    for transaction in transactions:
        await transaction_repository.create(transaction)
    
    return transactions


class TestDashboardService:
    """Testes do serviço principal de dashboard."""

    async def test_get_dashboard_balance(
        self, dashboard_service, user_id, sample_accounts
    ):
        """Testa a obtenção do saldo consolidado."""
        result = await dashboard_service.get_dashboard_balance(user_id)
        
        assert result.total_balance == Decimal("6500.00")
        assert len(result.accounts) == 2
        assert result.balance_by_type["checking"] == Decimal("1500.00")
        assert result.balance_by_type["savings"] == Decimal("5000.00")
        assert result.last_updated is not None

    async def test_get_dashboard_summary(
        self, dashboard_service, user_id, sample_transactions
    ):
        """Testa o resumo financeiro do período."""
        now = datetime.now()
        period_filter = PeriodFilter(
            start_date=now - timedelta(days=30),
            end_date=now
        )
        
        result = await dashboard_service.get_dashboard_summary(
            user_id, period_filter
        )
        
        assert result.total_income == Decimal("3000.00")
        assert result.total_expenses == Decimal("430.00")
        assert result.net_balance == Decimal("2570.00")
        assert result.total_transactions == 4
        assert result.income_transactions == 1
        assert result.expense_transactions == 3

    async def test_get_dashboard_expenses_by_category(
        self, dashboard_service, user_id, sample_transactions
    ):
        """Testa a distribuição de despesas por categoria."""
        now = datetime.now()
        category_filter = ExpensesCategoryFilter(
            start_date=now - timedelta(days=30),
            end_date=now,
            limit=10,
            include_others=True
        )
        
        result = await dashboard_service.get_dashboard_expenses_by_category(
            user_id, category_filter
        )
        
        assert result.total_expenses == Decimal("430.00")
        assert len(result.categories) <= 2  # Alimentação e Transporte
        
        # Categoria com maior gasto deve ser Alimentação (350.00)
        if result.categories:
            food_category = next(
                (c for c in result.categories if c.category_name == "Alimentação"),
                None
            )
            if food_category:
                assert food_category.total_amount == Decimal("350.00")

    async def test_get_dashboard_balance_evolution(
        self, dashboard_service, user_id, sample_accounts
    ):
        """Testa a evolução temporal dos saldos."""
        now = datetime.now()
        evolution_filter = BalanceEvolutionFilter(
            end_date=now,
            start_date=now - timedelta(days=365),
            granularity="monthly",
            months_back=12
        )
        
        result = await dashboard_service.get_dashboard_balance_evolution(
            user_id, evolution_filter
        )
        
        assert len(result.data_points) == 12
        assert result.granularity == "monthly"
        assert result.trend in ["growing", "stable", "declining"]

    async def test_get_dashboard_recent_transactions(
        self, dashboard_service, user_id, sample_transactions
    ):
        """Testa a obtenção de transações recentes."""
        result = await dashboard_service.get_dashboard_recent_transactions(
            user_id
        )
        
        assert len(result.transactions) <= 10
        assert result.total_recent_amount > Decimal("0")
        
        # Transações devem estar ordenadas por data (mais recente primeiro)
        if len(result.transactions) > 1:
            for i in range(len(result.transactions) - 1):
                assert (
                    result.transactions[i].date >= 
                    result.transactions[i + 1].date
                )

    async def test_get_dashboard_indicators(
        self, dashboard_service, user_id, sample_transactions
    ):
        """Testa a obtenção de indicadores e alertas."""
        result = await dashboard_service.get_dashboard_indicators(user_id)
        
        assert 0 <= result.financial_health_score <= 100
        assert isinstance(result.indicators, list)
        assert isinstance(result.alerts, list)
        assert isinstance(result.suggestions, list)


class TestFinancialAnalyticsService:
    """Testes do serviço de analytics financeiros."""

    async def test_calculate_financial_health_score(
        self, analytics_service, user_id, sample_transactions
    ):
        """Testa o cálculo do score de saúde financeira."""
        score = await analytics_service.calculate_financial_health_score(
            user_id
        )
        
        assert 0 <= score <= 100
        assert isinstance(score, int)

    async def test_generate_financial_indicators(
        self, analytics_service, user_id, sample_transactions
    ):
        """Testa a geração de indicadores financeiros."""
        indicators = await analytics_service.generate_financial_indicators(
            user_id
        )
        
        assert isinstance(indicators, list)
        
        if indicators:
            indicator = indicators[0]
            assert hasattr(indicator, 'name')
            assert hasattr(indicator, 'value')
            assert hasattr(indicator, 'status')

    async def test_detect_alerts(
        self, analytics_service, user_id, sample_accounts
    ):
        """Testa a detecção de alertas."""
        alerts = await analytics_service.detect_alerts(user_id)
        
        assert isinstance(alerts, list)

    async def test_generate_suggestions(
        self, analytics_service, user_id, sample_transactions
    ):
        """Testa a geração de sugestões."""
        suggestions = await analytics_service.generate_suggestions(user_id)
        
        assert isinstance(suggestions, list)
        
        if suggestions:
            suggestion = suggestions[0]
            assert hasattr(suggestion, 'title')
            assert hasattr(suggestion, 'description')


class TestDashboardEdgeCases:
    """Testes de casos extremos do dashboard."""

    async def test_dashboard_with_no_accounts(
        self, dashboard_service, user_id
    ):
        """Testa dashboard sem contas."""
        result = await dashboard_service.get_dashboard_balance(user_id)
        
        assert result.total_balance == Decimal("0")
        assert len(result.accounts) == 0
        assert result.balance_by_type == {}

    async def test_dashboard_with_no_transactions(
        self, dashboard_service, user_id, sample_accounts
    ):
        """Testa dashboard sem transações."""
        result = await dashboard_service.get_dashboard_summary(user_id)
        
        assert result.total_income == Decimal("0")
        assert result.total_expenses == Decimal("0")
        assert result.net_balance == Decimal("0")
        assert result.total_transactions == 0

    async def test_financial_health_no_data(
        self, analytics_service, user_id
    ):
        """Testa score de saúde sem dados."""
        score = await analytics_service.calculate_financial_health_score(
            user_id
        )
        
        # Deve retornar score neutro
        assert score == 50
