"""
Testes unitários para configurações da aplicação.

Testa o carregamento e validação das configurações.
"""

import os
from unittest.mock import patch

import pytest

from app.config import Settings, get_settings


class TestSettings:
    """Testes para a classe Settings."""
    
    def test_default_settings(self):
        """
        Testa as configurações padrão.
        
        Verifica se os valores padrão estão corretos.
        """
        settings = Settings()
        
        assert settings.environment == "dev"
        assert settings.debug is True
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.reload is True
        assert settings.app_name == "Financeiro Backend"
        assert settings.app_version == "0.1.0"
        assert settings.algorithm == "HS256"
        assert settings.access_token_expire_minutes == 30
    
    def test_mongodb_url_with_db_property(self):
        """
        Testa a propriedade mongodb_url_with_db.
        
        Verifica se a URL completa é construída corretamente.
        """
        settings = Settings()
        expected_url = f"{settings.mongodb_url}/{settings.mongodb_database}"
        assert settings.mongodb_url_with_db == expected_url
    
    def test_test_mongodb_url_with_db_property(self):
        """
        Testa a propriedade test_mongodb_url_with_db.
        
        Verifica se a URL de teste é construída corretamente.
        """
        settings = Settings()
        expected_url = f"{settings.test_mongodb_url}/{settings.test_mongodb_database}"
        assert settings.test_mongodb_url_with_db == expected_url
    
    def test_environment_detection_methods(self):
        """
        Testa os métodos de detecção de ambiente.
        
        Verifica se os métodos identificam corretamente o ambiente.
        """
        # Ambiente de desenvolvimento
        settings = Settings(environment="dev")
        assert settings.is_development() is True
        assert settings.is_production() is False
        assert settings.is_testing() is False
        
        # Ambiente de produção
        settings = Settings(environment="prod")
        assert settings.is_development() is False
        assert settings.is_production() is True
        assert settings.is_testing() is False
        
        # Ambiente de teste
        settings = Settings(environment="test")
        assert settings.is_development() is False
        assert settings.is_production() is False
        assert settings.is_testing() is True
    
    def test_secret_key_validation(self):
        """
        Testa a validação da chave secreta.
        
        Verifica se chaves muito curtas são rejeitadas.
        """
        # Chave válida (32+ caracteres)
        valid_key = "a" * 32
        settings = Settings(secret_key=valid_key)
        assert settings.secret_key == valid_key
        
        # Chave muito curta deve gerar erro
        with pytest.raises(ValueError, match="SECRET_KEY deve ter pelo menos 32 caracteres"):
            Settings(secret_key="short")
    
    def test_log_level_validation(self):
        """
        Testa a validação do nível de log.
        
        Verifica se apenas níveis válidos são aceitos.
        """
        # Níveis válidos
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in valid_levels:
            settings = Settings(log_level=level)
            assert settings.log_level == level.upper()
        
        # Nível inválido deve gerar erro
        with pytest.raises(ValueError, match="LOG_LEVEL deve ser um de"):
            Settings(log_level="INVALID")
    
    def test_cors_origins_parsing(self):
        """
        Testa o parsing das origens CORS.
        
        Verifica se strings com vírgulas são convertidas em listas.
        """
        # Lista direta
        origins_list = ["http://localhost:3000", "http://localhost:8080"]
        settings = Settings(cors_origins=origins_list)
        assert settings.cors_origins == origins_list
        
        # String com vírgulas
        origins_string = "http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000"
        settings = Settings(cors_origins=origins_string)
        expected_list = ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]
        assert settings.cors_origins == expected_list
    
    @patch.dict(os.environ, {
        "ENVIRONMENT": "prod",
        "DEBUG": "false",
        "SECRET_KEY": "production-secret-key-32-characters-long",
        "MONGODB_URL": "mongodb://prod-server:27017",
        "LOG_LEVEL": "WARNING"
    })
    def test_environment_variables_override(self):
        """
        Testa se variáveis de ambiente sobrescrevem os padrões.
        
        Verifica se as configurações são carregadas do ambiente.
        """
        settings = Settings()
        
        assert settings.environment == "prod"
        assert settings.debug is False
        assert settings.secret_key == "production-secret-key-32-characters-long"
        assert settings.mongodb_url == "mongodb://prod-server:27017"
        assert settings.log_level == "WARNING"


class TestGetSettings:
    """Testes para a função get_settings."""
    
    def test_get_settings_returns_singleton(self):
        """
        Testa se get_settings retorna sempre a mesma instância.
        
        Verifica o comportamento de singleton.
        """
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2
        assert id(settings1) == id(settings2)
    
    def test_get_settings_returns_settings_instance(self):
        """
        Testa se get_settings retorna uma instância de Settings.
        """
        settings = get_settings()
        assert isinstance(settings, Settings)
