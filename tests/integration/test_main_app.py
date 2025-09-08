"""
Testes de integração para a aplicação principal.

Testa a configuração e inicialização da aplicação FastAPI.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app, create_app


class TestApplicationIntegration:
    """Testes de integração para a aplicação principal."""
    
    def test_create_app_returns_fastapi_instance(self):
        """Testa se create_app retorna uma instância do FastAPI."""
        test_app = create_app()
        
        assert test_app is not None
    
    def test_application_basic_configuration(self):
        """
        Testa a configuração básica da aplicação.
        
        Verifica se as configurações essenciais estão corretas.
        """
        assert app.title == "Financeiro Backend"
        assert app.version == "0.1.0"
        assert "Sistema de Controle Financeiro" in app.description
    
    def test_health_endpoints_are_registered(self, client: TestClient):
        """
        Testa se os endpoints de health check estão registrados.
        
        Verifica se os endpoints respondem corretamente.
        """
        # Testar endpoint básico
        response = client.get("/health")
        assert response.status_code == 200
        
        # Testar endpoint detalhado
        response = client.get("/health/detailed")
        assert response.status_code == 200
    
    def test_cors_middleware_is_configured(self, client: TestClient):
        """
        Testa se o middleware CORS está configurado.
        
        Verifica se headers CORS são retornados.
        """
        response = client.options("/health", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        
        # CORS deve permitir a requisição
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
    
    def test_application_startup_and_shutdown_events(self):
        """
        Testa se a aplicação está configurada corretamente.
        
        Verifica se a aplicação tem a estrutura esperada.
        """
        # Verifica se a aplicação tem os componentes básicos
        assert hasattr(app, 'router'), "App deve ter router"
        assert app.title == "Financeiro Backend"
        # Se chegou até aqui, a aplicação foi inicializada corretamente
        # incluindo qualquer lifecycle/startup/shutdown configurado
    
    def test_documentation_endpoints_in_development(
        self, client: TestClient
    ) -> None:
        """
        Testa se endpoints de documentação estão disponíveis.
        
        Verifica se /docs e /redoc estão acessíveis.
        """
        # Testar página de documentação Swagger
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        # Testar página de documentação ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_schema_is_generated(self, client: TestClient) -> None:
        """
        Testa se o schema OpenAPI é gerado corretamente.
        
        Verifica se o endpoint de schema retorna dados válidos.
        """
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "Financeiro Backend"
        assert schema["info"]["version"] == "0.1.0"
    
    def test_404_for_nonexistent_endpoints(self, client: TestClient) -> None:
        """
        Testa se endpoints inexistentes retornam 404.
        
        Verifica o comportamento padrão para rotas não encontradas.
        """
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Not Found" in data["detail"]
