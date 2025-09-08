"""
Testes unitários para o health check controller.

Testa o funcionamento dos endpoints de verificação de saúde da aplicação.
"""

from fastapi.testclient import TestClient


class TestHealthController:
    """Testes para os endpoints de health check."""

    def test_basic_health_check(self, client: TestClient):
        """
        Testa o endpoint básico de health check.

        Verifica se:
        - Retorna status code 200
        - Retorna status "OK"
        - Contém informações básicas da aplicação
        """
        response = client.get("/health")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "OK"
        assert "service" in data
        assert "version" in data
        assert "environment" in data
        assert "timestamp" in data
        assert "uptime" in data

    def test_detailed_health_check(self, client: TestClient):
        """
        Testa o endpoint detalhado de health check.

        Verifica se:
        - Retorna status code 200
        - Contém todas as informações básicas
        - Inclui informações de dependências
        - Inclui configurações da aplicação
        """
        response = client.get("/health/detailed")

        assert response.status_code == 200

        data = response.json()

        # Verificar estrutura básica
        assert data["status"] == "OK"
        assert "service" in data
        assert "version" in data
        assert "environment" in data
        assert "timestamp" in data

        # Verificar dependências
        assert "dependencies" in data
        assert "mongodb" in data["dependencies"]
        assert "redis" in data["dependencies"]

        # Verificar configurações
        assert "configuration" in data
        assert "debug" in data["configuration"]
        assert "cors_origins" in data["configuration"]
        assert "log_level" in data["configuration"]

    def test_health_check_response_format(self, client: TestClient):
        """
        Testa o formato da resposta do health check.

        Verifica se os campos têm os tipos corretos.
        """
        response = client.get("/health")
        data = response.json()

        # Verificar tipos dos campos
        assert isinstance(data["status"], str)
        assert isinstance(data["service"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["environment"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["uptime"], str)

    def test_detailed_health_check_structure(self, client: TestClient):
        """
        Testa a estrutura detalhada do health check.

        Verifica se todas as seções obrigatórias estão presentes.
        """
        response = client.get("/health/detailed")
        data = response.json()

        # Verificar estrutura de dependências
        dependencies = data["dependencies"]

        # MongoDB
        mongodb = dependencies["mongodb"]
        assert "status" in mongodb
        assert "url" in mongodb
        assert "database" in mongodb

        # Redis
        redis = dependencies["redis"]
        assert "status" in redis
        assert "url" in redis

        # Configurações
        config = data["configuration"]
        assert isinstance(config["debug"], bool)
        assert isinstance(config["cors_origins"], list)
        assert isinstance(config["log_level"], str)

    def test_health_endpoints_are_public(self, client: TestClient):
        """
        Verifica se os endpoints de health check são públicos.

        Os endpoints de health check não devem requerer autenticação.
        """
        # Endpoint básico
        response = client.get("/health")
        assert response.status_code == 200

        # Endpoint detalhado
        response = client.get("/health/detailed")
        assert response.status_code == 200
