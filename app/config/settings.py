"""
Configurações centralizadas da aplicação.

Este módulo gerencia todas as configurações do sistema usando Pydantic Settings,
permitindo carregamento automático de variáveis de ambiente e validação.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas automaticamente do ambiente.
    
    Todas as configurações podem ser sobrescritas por variáveis de ambiente
    com o prefixo configurado ou através de arquivo .env.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # =================================
    # CONFIGURAÇÕES GERAIS
    # =================================
    
    environment: str = Field(default="dev", description="Ambiente de execução")
    debug: bool = Field(default=True, description="Modo debug")
    
    # Configurações do servidor
    host: str = Field(default="0.0.0.0", description="Host do servidor")
    port: int = Field(default=8000, description="Porta do servidor")
    reload: bool = Field(default=True, description="Auto-reload em desenvolvimento")
    
    # Informações da aplicação
    app_name: str = Field(default="Financeiro Backend", description="Nome da aplicação")
    app_version: str = Field(default="0.1.0", description="Versão da aplicação")
    app_description: str = Field(
        default="Sistema de Controle Financeiro Pessoal - API Backend",
        description="Descrição da aplicação"
    )
    
    # =================================
    # CONFIGURAÇÕES DE SEGURANÇA
    # =================================
    
    secret_key: str = Field(
        default="your-super-secret-key-change-this-in-production-32-chars-minimum",
        description="Chave secreta para JWT"
    )
    algorithm: str = Field(default="HS256", description="Algoritmo de criptografia JWT")
    access_token_expire_minutes: int = Field(
        default=30, 
        description="Tempo de expiração do token de acesso em minutos"
    )
    
    @property
    def access_token_expire_seconds(self) -> int:
        """Retorna o tempo de expiração do token em segundos."""
        return self.access_token_expire_minutes * 60
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Valida se a chave secreta tem tamanho mínimo adequado."""
        if len(v) < 32:
            raise ValueError("SECRET_KEY deve ter pelo menos 32 caracteres")
        return v
    
    # =================================
    # CONFIGURAÇÕES DO BANCO DE DADOS
    # =================================
    
    # MongoDB
    mongodb_url: str = Field(
        default="mongodb://localhost:27017",
        description="URL de conexão com MongoDB"
    )
    mongodb_database: str = Field(
        default="financeiro_db",
        description="Nome do banco de dados"
    )
    mongodb_min_connections: int = Field(
        default=10,
        description="Número mínimo de conexões no pool"
    )
    mongodb_max_connections: int = Field(
        default=100,
        description="Número máximo de conexões no pool"
    )
    
    @property
    def mongodb_url_with_db(self) -> str:
        """URL completa do MongoDB incluindo o banco de dados."""
        return f"{self.mongodb_url}/{self.mongodb_database}"
    
    # =================================
    # CONFIGURAÇÕES DO REDIS
    # =================================
    
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="URL de conexão com Redis"
    )
    redis_ttl: int = Field(
        default=3600,
        description="TTL padrão para cache em segundos"
    )
    
    # =================================
    # CONFIGURAÇÕES DE LOG
    # =================================
    
    log_level: str = Field(default="INFO", description="Nível de log")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Formato do log"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Valida se o nível de log é válido."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL deve ser um de: {', '.join(valid_levels)}")
        return v.upper()
    
    # =================================
    # CONFIGURAÇÕES DE CORS
    # =================================
    
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8080", 
            "http://127.0.0.1:3000"
        ],
        description="URLs permitidas para CORS"
    )
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse das origens CORS se fornecidas como string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        return v
    
    # =================================
    # CONFIGURAÇÕES DE EMAIL
    # =================================
    
    smtp_host: Optional[str] = Field(default=None, description="Host SMTP")
    smtp_port: int = Field(default=587, description="Porta SMTP")
    smtp_user: Optional[str] = Field(default=None, description="Usuário SMTP")
    smtp_password: Optional[str] = Field(default=None, description="Senha SMTP")
    smtp_tls: bool = Field(default=True, description="Usar TLS no SMTP")
    
    # =================================
    # CONFIGURAÇÕES DE TESTE
    # =================================
    
    test_mongodb_url: str = Field(
        default="mongodb://localhost:27017",
        description="URL MongoDB para testes"
    )
    test_mongodb_database: str = Field(
        default="financeiro_test_db",
        description="Banco de dados para testes"
    )
    test_redis_url: str = Field(
        default="redis://localhost:6379/1",
        description="URL Redis para testes"
    )
    
    @property
    def test_mongodb_url_with_db(self) -> str:
        """URL completa do MongoDB para testes incluindo o banco."""
        return f"{self.test_mongodb_url}/{self.test_mongodb_database}"
    
    # =================================
    # MÉTODOS AUXILIARES
    # =================================
    
    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento."""
        return self.environment.lower() == "dev"
    
    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção."""
        return self.environment.lower() == "prod"
    
    def is_testing(self) -> bool:
        """Verifica se está em ambiente de teste."""
        return self.environment.lower() == "test"


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna uma instância singleton das configurações.
    
    Usa cache para evitar recarregar as configurações múltiplas vezes.
    
    Returns:
        Settings: Instância das configurações da aplicação
    """
    return Settings()


# Instância global das configurações para facilitar importação
settings = get_settings()
