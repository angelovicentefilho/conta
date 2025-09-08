"""
Testes de integração para os controladores de dashboard.

Testa os endpoints REST do dashboard com dados reais.
"""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app


def get_auth_headers(client):
    """Função auxiliar para autenticação nos testes."""
    # Registrar usuário
    register_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "TestPassword123!",
    }

    response = client.post("/auth/register", json=register_data)
    # 200 se já existe, 201 se criado
    assert response.status_code in [200, 201]

    # Fazer login
    login_data = {"email": "test@example.com", "password": "TestPassword123!"}

    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestDashboardControllers:
    """Testes dos controladores de dashboard."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup para cada teste."""
        self.client = TestClient(app)
        self.auth_headers = get_auth_headers(self.client)

    def teardown_method(self):
        """Cleanup após cada teste."""

    async def test_get_dashboard_balance_success(self):
        """Testa endpoint de saldo do dashboard com sucesso."""
        response = self.client.get(
            "/dashboard/balance", headers=self.auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "total_balance" in data
        assert "balance_by_type" in data
        assert "accounts" in data
        assert "last_updated" in data

        assert isinstance(data["total_balance"], (int, float, str))
        assert isinstance(data["balance_by_type"], dict)
        assert isinstance(data["accounts"], list)

    async def test_get_dashboard_summary_success(self):
        """Testa endpoint de resumo do dashboard com sucesso."""
        response = self.client.get(
            "/dashboard/summary", headers=self.auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        required_fields = [
            "period_start",
            "period_end",
            "total_income",
            "total_expenses",
            "net_balance",
            "highest_income",
            "highest_expense",
            "daily_average_income",
            "daily_average_expenses",
            "total_transactions",
            "income_transactions",
            "expense_transactions",
        ]

        for field in required_fields:
            assert field in data

    async def test_get_dashboard_summary_with_dates(self):
        """Testa endpoint de resumo com datas específicas."""
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        response = self.client.get(
            "/dashboard/summary",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            headers=self.auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert "period_start" in data
        assert "period_end" in data

    async def test_get_dashboard_expenses_by_category_success(self):
        """Testa endpoint de despesas por categoria com sucesso."""
        response = self.client.get(
            "/dashboard/expenses-by-category", headers=self.auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "period_start" in data
        assert "period_end" in data
        assert "total_expenses" in data
        assert "categories" in data
        assert "others_amount" in data
        assert "others_percentage" in data

        assert isinstance(data["categories"], list)

    async def test_get_dashboard_expenses_by_category_with_params(self):
        """Testa endpoint de despesas por categoria com parâmetros."""
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        response = self.client.get(
            "/dashboard/expenses-by-category",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "limit": 5,
                "include_others": True,
            },
            headers=self.auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["categories"]) <= 5

    async def test_get_dashboard_balance_evolution_success(self):
        """Testa endpoint de evolução de saldos com sucesso."""
        response = self.client.get(
            "/dashboard/balance-evolution", headers=self.auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "period_start" in data
        assert "period_end" in data
        assert "granularity" in data
        assert "data_points" in data
        assert "trend" in data
        assert "trend_percentage" in data

        assert isinstance(data["data_points"], list)
        assert data["trend"] in ["growing", "stable", "declining"]

    async def test_get_dashboard_balance_evolution_with_params(self):
        """Testa endpoint de evolução com parâmetros."""
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()

        response = self.client.get(
            "/dashboard/balance-evolution",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "granularity": "monthly",
                "months_back": 6,
            },
            headers=self.auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["granularity"] == "monthly"

    async def test_get_dashboard_recent_transactions_success(self):
        """Testa endpoint de transações recentes com sucesso."""
        response = self.client.get(
            "/dashboard/recent-transactions", headers=self.auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "transactions" in data
        assert "total_recent_amount" in data

        assert isinstance(data["transactions"], list)

        # Verificar estrutura das transações se existirem
        if data["transactions"]:
            transaction = data["transactions"][0]
            required_fields = [
                "id",
                "date",
                "description",
                "amount",
                "type",
                "account_name",
                "category_name",
            ]

            for field in required_fields:
                assert field in transaction

    async def test_get_dashboard_indicators_success(self):
        """Testa endpoint de indicadores com sucesso."""
        response = self.client.get(
            "/dashboard/indicators", headers=self.auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "financial_health_score" in data
        assert "indicators" in data
        assert "alerts" in data
        assert "suggestions" in data

        assert isinstance(data["financial_health_score"], int)
        assert 0 <= data["financial_health_score"] <= 100
        assert isinstance(data["indicators"], list)
        assert isinstance(data["alerts"], list)
        assert isinstance(data["suggestions"], list)

    async def test_dashboard_endpoints_without_auth(self):
        """Testa endpoints sem autenticação."""
        endpoints = [
            "/dashboard/balance",
            "/dashboard/summary",
            "/dashboard/expenses-by-category",
            "/dashboard/balance-evolution",
            "/dashboard/recent-transactions",
            "/dashboard/indicators",
        ]

        for endpoint in endpoints:
            response = self.client.get(endpoint)  # Sem headers
            # Deve retornar erro de autenticação
            assert response.status_code in [401, 403]

    async def test_dashboard_balance_evolution_invalid_granularity(self):
        """Testa evolução com granularidade inválida."""
        response = self.client.get(
            "/dashboard/balance-evolution",
            params={"granularity": "invalid"},
            headers=self.auth_headers,
        )

        # Deve retornar erro de validação
        assert response.status_code == 422

    async def test_dashboard_expenses_category_invalid_limit(self):
        """Testa despesas por categoria com limite inválido."""
        response = self.client.get(
            "/dashboard/expenses-by-category",
            params={"limit": 0},
            headers=self.auth_headers,
        )

        # Deve retornar erro de validação
        assert response.status_code == 422

    async def test_dashboard_expenses_category_limit_too_high(self):
        """Testa despesas por categoria com limite muito alto."""
        response = self.client.get(
            "/dashboard/expenses-by-category",
            params={"limit": 100},
            headers=self.auth_headers,
        )

        # Deve retornar erro de validação
        assert response.status_code == 422

    async def test_dashboard_balance_evolution_invalid_months_back(self):
        """Testa evolução com months_back inválido."""
        response = self.client.get(
            "/dashboard/balance-evolution",
            params={"months_back": 0},
            headers=self.auth_headers,
        )

        # Deve retornar erro de validação
        assert response.status_code == 422

    async def test_dashboard_balance_evolution_months_back_too_high(self):
        """Testa evolução com months_back muito alto."""
        response = self.client.get(
            "/dashboard/balance-evolution",
            params={"months_back": 50},
            headers=self.auth_headers,
        )

        # Deve retornar erro de validação
        assert response.status_code == 422


class TestDashboardValidation:
    """Testes específicos de validação dos endpoints."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup para cada teste."""
        self.client = TestClient(app)
        self.auth_headers = get_auth_headers(self.client)

    def teardown_method(self):
        """Cleanup após cada teste."""

    async def test_summary_invalid_date_format(self):
        """Testa summary com formato de data inválido."""
        response = self.client.get(
            "/dashboard/summary",
            params={
                "start_date": "invalid-date",
                "end_date": "2024-01-01T00:00:00",
            },
            headers=self.auth_headers,
        )

        assert response.status_code == 422

    async def test_expenses_category_invalid_date_format(self):
        """Testa expenses-by-category com formato de data inválido."""
        response = self.client.get(
            "/dashboard/expenses-by-category",
            params={
                "start_date": "2024-13-50",  # Data inválida
                "end_date": "2024-01-01T00:00:00",
            },
            headers=self.auth_headers,
        )

        assert response.status_code == 422

    async def test_balance_evolution_invalid_date_format(self):
        """Testa balance-evolution com formato de data inválido."""
        response = self.client.get(
            "/dashboard/balance-evolution",
            params={
                "start_date": "not-a-date",
                "end_date": "2024-01-01T00:00:00",
            },
            headers=self.auth_headers,
        )

        assert response.status_code == 422


class TestDashboardPerformance:
    """Testes de performance dos endpoints de dashboard."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup para cada teste."""
        self.client = TestClient(app)
        self.auth_headers = get_auth_headers(self.client)

    def teardown_method(self):
        """Cleanup após cada teste."""

    async def test_dashboard_endpoints_response_time(self):
        """Testa tempo de resposta dos endpoints."""
        import time

        endpoints = [
            "/dashboard/balance",
            "/dashboard/summary",
            "/dashboard/recent-transactions",
            "/dashboard/indicators",
        ]

        for endpoint in endpoints:
            start_time = time.time()
            response = self.client.get(endpoint, headers=self.auth_headers)
            end_time = time.time()

            assert response.status_code == 200
            # Endpoints devem responder em menos de 2 segundos
            assert (end_time - start_time) < 2.0
