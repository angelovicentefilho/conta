# =====================================
# Makefile para Sistema Financeiro Backend
# =====================================
#
# Este Makefile fornece comandos para desenvolvimento, teste e deploy
# da aplicação de controle financeiro seguindo boas práticas.
#
# Uso: make <comando>
# Para ver todos os comandos disponíveis: make help

.PHONY: help setup install install-dev dev run stop test test-cov lint format clean clean-pycache build docker-build docker-run services-up services-down services-logs services-status mongo-up mongo-down mongo-logs redis-up redis-down redis-logs

# Configurações
PYTHON := python3.12
VENV_PATH := .venv
PIP := $(VENV_PATH)/bin/pip
PYTHON_VENV := $(VENV_PATH)/bin/python
UVICORN := $(VENV_PATH)/bin/uvicorn
PYTEST := $(VENV_PATH)/bin/pytest
BLACK := $(VENV_PATH)/bin/black
ISORT := $(VENV_PATH)/bin/isort
FLAKE8 := $(VENV_PATH)/bin/flake8
MYPY := $(VENV_PATH)/bin/mypy

# Cores para output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[0;37m
NC := \033[0m

# =====================================
# COMANDO PRINCIPAL: HELP
# =====================================

help: ## 📖 Mostra esta mensagem de ajuda
	@echo "$(CYAN)========================================$(NC)"
	@echo "$(CYAN)🚀 Sistema Financeiro Backend - Makefile$(NC)"
	@echo "$(CYAN)========================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Comandos disponíveis:$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BLUE)Exemplos de uso:$(NC)"
	@echo "  make setup      # Configuração inicial completa"
	@echo "  make dev        # Inicia servidor de desenvolvimento"
	@echo "  make test       # Executa todos os testes"
	@echo "  make clean-pycache # Remove apenas arquivos __pycache__ e *.pyc"
	@echo "  make lint       # Verifica qualidade do código"
	@echo ""

# =====================================
# SETUP E INSTALAÇÃO
# =====================================

setup: ## 🔧 Configuração inicial completa do projeto (recomendado para novo ambiente)
	@echo "$(YELLOW)🔧 Iniciando configuração do projeto...$(NC)"
	@$(MAKE) check-python
	@$(MAKE) create-venv
	@$(MAKE) install-dev
	@$(MAKE) create-env
	@echo "$(GREEN)✅ Configuração completa! Use 'make dev' para iniciar.$(NC)"

check-python: ## ✓ Verifica se Python 3.12+ está disponível
	@echo "$(BLUE)🔍 Verificando Python 3.12+...$(NC)"
	@which $(PYTHON) > /dev/null || (echo "$(RED)❌ Python 3.12+ não encontrado!$(NC)" && exit 1)
	@$(PYTHON) --version | grep -E "Python 3\.(1[2-9]|[2-9][0-9])" > /dev/null || (echo "$(RED)❌ Python 3.12+ necessário!$(NC)" && exit 1)
	@echo "$(GREEN)✅ Python $(shell $(PYTHON) --version | cut -d' ' -f2) encontrado$(NC)"

create-venv: ## 🐍 Cria ambiente virtual Python isolado
	@echo "$(BLUE)🐍 Criando ambiente virtual...$(NC)"
	@if [ ! -d "$(VENV_PATH)" ]; then \
		$(PYTHON) -m venv $(VENV_PATH); \
		echo "$(GREEN)✅ Ambiente virtual criado em $(VENV_PATH)$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Ambiente virtual já existe$(NC)"; \
	fi

install: ## 📦 Instala dependências de produção no .venv
	@echo "$(BLUE)📦 Instalando dependências de produção...$(NC)"
	@$(MAKE) check-venv
	@$(PIP) install --upgrade pip
	@$(PIP) install -e .
	@echo "$(GREEN)✅ Dependências de produção instaladas$(NC)"

install-dev: ## 🛠️ Instala dependências de desenvolvimento no .venv
	@echo "$(BLUE)🛠️  Instalando dependências de desenvolvimento...$(NC)"
	@$(MAKE) check-venv
	@$(PIP) install --upgrade pip
	@$(PIP) install -e ".[dev]"
	@echo "$(GREEN)✅ Dependências de desenvolvimento instaladas$(NC)"

check-venv: ## ✓ Verifica se ambiente virtual existe
	@if [ ! -d "$(VENV_PATH)" ]; then \
		echo "$(RED)❌ Ambiente virtual não encontrado! Execute 'make setup'$(NC)"; \
		exit 1; \
	fi

create-env: ## 📝 Cria arquivo .env a partir do .env.example (se não existir)
	@if [ ! -f ".env" ]; then \
		echo "$(BLUE)📝 Criando arquivo .env...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN)✅ Arquivo .env criado$(NC)"; \
		echo "$(YELLOW)⚠️  Lembre-se de configurar as variáveis em .env$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Arquivo .env já existe$(NC)"; \
	fi

# =====================================
# DESENVOLVIMENTO
# =====================================

dev: ## 🚀 Inicia servidor de desenvolvimento com auto-reload
	@$(MAKE) check-venv
	@echo ""
	@$(PYTHON_VENV) scripts/print_banner_gradient.py
	@echo ""
	@$(PYTHON_VENV) scripts/print_status_table.py
	@echo ""
	@echo "$(CYAN)📡 Servidor disponível em: http://localhost:8000$(NC)"
	@echo "$(CYAN)📚 Documentação em: http://localhost:8000/docs$(NC)"
	@echo "$(CYAN)🛑 Para parar: Ctrl+C$(NC)"
	@echo ""
	@$(UVICORN) app.main:app --host 0.0.0.0 --port 8000 --reload

run: ## ▶️ Inicia servidor em modo produção
	@$(MAKE) check-venv
	@echo ""
	@$(PYTHON_VENV) scripts/print_banner_gradient.py
	@echo ""
	@$(PYTHON_VENV) scripts/print_status_table.py
	@echo ""
	@echo "$(CYAN)📡 Servidor disponível em: http://localhost:8000$(NC)"
	@echo "$(CYAN)📚 Documentação em: http://localhost:8000/docs$(NC)"
	@echo "$(CYAN)🛑 Para parar: Ctrl+C$(NC)"
	@echo ""
	@$(UVICORN) app.main:app --host 0.0.0.0 --port 8000

stop: ## 🛑 Para todos os processos da aplicação
	@echo "$(YELLOW)🛑 Parando aplicação...$(NC)"
	@echo "$(BLUE)🔍 Procurando processos do Uvicorn na porta 8000...$(NC)"
	@-pkill -f "uvicorn.*app.main:app" 2>/dev/null && echo "$(GREEN)✅ Processos Uvicorn finalizados$(NC)" || echo "$(YELLOW)⚠️  Nenhum processo Uvicorn encontrado$(NC)"
	@-lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "$(GREEN)✅ Porta 8000 liberada$(NC)" || echo "$(YELLOW)⚠️  Porta 8000 já está livre$(NC)"
	@echo "$(GREEN)✅ Aplicação parada com sucesso!$(NC)"

# =====================================
# TESTES
# =====================================

test: ## 🧪 Executa todos os testes
	@echo "$(BLUE)🧪 Executando testes...$(NC)"
	@$(MAKE) check-venv
	@$(PYTEST) tests/ -v

test-cov: ## 📊 Executa testes com relatório de cobertura
	@echo "$(BLUE)📊 Executando testes com cobertura...$(NC)"
	@$(MAKE) check-venv
	@$(PYTEST) tests/ -v --cov=app --cov-report=html --cov-report=term

test-unit: ## 🔬 Executa apenas testes unitários
	@echo "$(BLUE)🔬 Executando testes unitários...$(NC)"
	@$(MAKE) check-venv
	@$(PYTEST) tests/unit/ -v

test-integration: ## 🔗 Executa apenas testes de integração
	@echo "$(BLUE)🔗 Executando testes de integração...$(NC)"
	@$(MAKE) check-venv
	@$(PYTEST) tests/integration/ -v

# =====================================
# QUALIDADE DE CÓDIGO
# =====================================

lint: ## 🔍 Verifica qualidade do código (flake8 + mypy)
	@echo "$(BLUE)🔍 Verificando qualidade do código...$(NC)"
	@$(MAKE) check-venv
	@echo "$(CYAN)📝 Executando flake8...$(NC)"
	@$(FLAKE8) app tests
	@echo "$(CYAN)🔬 Executando mypy...$(NC)"
	@$(MYPY) app
	@echo "$(GREEN)✅ Verificação de qualidade concluída$(NC)"

format: ## 🎨 Formata código (black + isort)
	@echo "$(BLUE)🎨 Formatando código...$(NC)"
	@$(MAKE) check-venv
	@echo "$(CYAN)🔤 Executando isort...$(NC)"
	@$(ISORT) app tests
	@echo "$(CYAN)⚫ Executando black...$(NC)"
	@$(BLACK) app tests
	@echo "$(GREEN)✅ Formatação concluída$(NC)"

format-check: ## ✓ Verifica se código está formatado corretamente
	@echo "$(BLUE)✓ Verificando formatação...$(NC)"
	@$(MAKE) check-venv
	@$(BLACK) --check app tests
	@$(ISORT) --check-only app tests
	@echo "$(GREEN)✅ Código está bem formatado$(NC)"

# =====================================
# LIMPEZA
# =====================================

clean: ## 🧹 Remove arquivos temporários e cache
	@echo "$(BLUE)🧹 Limpando arquivos temporários...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*~" -delete
	@find . -type f -name "__pycache__" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete
	@rm -rf build/ dist/ htmlcov/ .coverage .coverage.*
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@find . -type f -name "*.tmp" -delete 2>/dev/null || true
	@find . -type f -name "*.temp" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@find . -type f -name "Thumbs.db" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Limpeza concluída$(NC)"

clean-pycache: ## 🧼 Remove apenas arquivos __pycache__ e *.pyc
	@echo "$(BLUE)🧼 Removendo apenas arquivos __pycache__ e *.pyc...$(NC)"
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.pyd" -delete 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Limpeza de pycache concluída$(NC)"

clean-all: ## 🗑️ Remove TUDO (incluindo .venv) - USE COM CUIDADO!
	@echo "$(RED)🗑️  ATENÇÃO: Removendo TUDO incluindo ambiente virtual!$(NC)"
	@read -p "Tem certeza? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@$(MAKE) clean
	@rm -rf $(VENV_PATH)
	@rm -f .env
	@echo "$(GREEN)✅ Limpeza completa realizada$(NC)"

# =====================================
# DOCKER E SERVIÇOS
# =====================================

services-up: ## 🐳 Inicia todos os serviços (MongoDB + Redis)
	@echo "$(BLUE)🐳 Iniciando todos os serviços...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✅ Serviços iniciados com sucesso!$(NC)"
	@echo "$(CYAN)📊 MongoDB: mongodb://localhost:27017$(NC)"
	@echo "$(CYAN)🚀 Redis: redis://localhost:6379$(NC)"

services-down: ## 🛑 Para todos os serviços (MongoDB + Redis)
	@echo "$(YELLOW)🛑 Parando todos os serviços...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✅ Serviços parados com sucesso!$(NC)"

services-logs: ## 📋 Mostra logs dos serviços
	@echo "$(BLUE)📋 Mostrando logs dos serviços...$(NC)"
	@docker-compose logs -f

services-status: ## 📊 Mostra status dos serviços
	@echo "$(CYAN)📊 Status dos Serviços$(NC)"
	@echo "$(CYAN)========================================$(NC)"
	@docker-compose ps

mongo-up: ## 🍃 Inicia apenas o MongoDB
	@echo "$(BLUE)🍃 Iniciando MongoDB...$(NC)"
	@docker-compose up -d mongodb
	@echo "$(GREEN)✅ MongoDB iniciado!$(NC)"
	@echo "$(CYAN)📊 Disponível em: mongodb://localhost:27017$(NC)"

mongo-down: ## 🛑 Para apenas o MongoDB
	@echo "$(YELLOW)🛑 Parando MongoDB...$(NC)"
	@docker-compose stop mongodb
	@echo "$(GREEN)✅ MongoDB parado!$(NC)"

mongo-logs: ## 📋 Mostra logs do MongoDB
	@docker-compose logs -f mongodb

redis-up: ## 🚀 Inicia apenas o Redis
	@echo "$(BLUE)🚀 Iniciando Redis...$(NC)"
	@docker-compose up -d redis
	@echo "$(GREEN)✅ Redis iniciado!$(NC)"
	@echo "$(CYAN)🚀 Disponível em: redis://localhost:6379$(NC)"

redis-down: ## 🛑 Para apenas o Redis
	@echo "$(YELLOW)🛑 Parando Redis...$(NC)"
	@docker-compose stop redis
	@echo "$(GREEN)✅ Redis parado!$(NC)"

redis-logs: ## 📋 Mostra logs do Redis
	@docker-compose logs -f redis

# =====================================
# INFORMAÇÕES
# =====================================

status: ## 📋 Mostra status do projeto
	@echo "$(CYAN)========================================$(NC)"
	@echo "$(CYAN)📋 Status do Projeto$(NC)"
	@echo "$(CYAN)========================================$(NC)"
	@echo ""
	@echo "$(YELLOW)🐍 Python:$(NC)"
	@which $(PYTHON) && $(PYTHON) --version || echo "$(RED)❌ Python 3.12+ não encontrado$(NC)"
	@echo ""
	@echo "$(YELLOW)🌍 Ambiente Virtual:$(NC)"
	@if [ -d "$(VENV_PATH)" ]; then \
		echo "$(GREEN)✅ Ambiente virtual existe em $(VENV_PATH)$(NC)"; \
		echo "$(BLUE)📦 Pip: $(shell $(PIP) --version 2>/dev/null || echo 'não instalado')$(NC)"; \
	else \
		echo "$(RED)❌ Ambiente virtual não encontrado$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)📁 Arquivos:$(NC)"
	@[ -f ".env" ] && echo "$(GREEN)✅ .env existe$(NC)" || echo "$(YELLOW)⚠️  .env não encontrado$(NC)"
	@[ -f "pyproject.toml" ] && echo "$(GREEN)✅ pyproject.toml existe$(NC)" || echo "$(RED)❌ pyproject.toml não encontrado$(NC)"
	@echo ""

# =====================================
# TARGET PADRÃO
# =====================================

.DEFAULT_GOAL := help
