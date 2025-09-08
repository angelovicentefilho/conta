# 💰 Sistema Financeiro Backend

Sistema de controle financeiro pessoal desenvolvido com **FastAPI** seguindo os princípios da **Arquitetura Hexagonal** (Ports & Adapters).

## 🏗️ Arquitetura

```
app/
├── core/                    # 🎯 Núcleo da aplicação
│   ├── domain/             # 📋 Entidades e objetos de valor
│   ├── ports/              # 🔌 Interfaces (portas)
│   └── services/           # ⚙️ Lógica de negócio
├── adapters/               # 🔄 Adaptadores
│   ├── inbound/           # 📥 Entrada (APIs, Controllers)
│   └── outbound/          # 📤 Saída (BD, Serviços externos)
├── config/                 # ⚙️ Configurações
└── main.py                 # 🚀 Aplicação principal
```

## 🚀 Quick Start

### 1. Pré-requisitos

- **Python 3.12+** 
- **MongoDB** (local ou Docker)
- **Redis** (local ou Docker)

### 2. Configuração Inicial

```bash
# Clone o repositório
git clone <repository-url>
cd financeiro/backend

# Configuração automática completa
make setup
```

O comando `make setup` irá:
- ✅ Verificar Python 3.12+
- ✅ Criar ambiente virtual isolado (`.venv`)
- ✅ Instalar todas as dependências
- ✅ Criar arquivo `.env` a partir do template

### 3. Configurar Variáveis de Ambiente

Edite o arquivo `.env` criado automaticamente:

```bash
# Edite as configurações conforme seu ambiente
nano .env
```

**Configurações principais:**

```env
# Banco de dados
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=financeiro_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Segurança (MUDE EM PRODUÇÃO!)
SECRET_KEY=sua-chave-super-secreta-de-32-caracteres-ou-mais
```

### 4. Executar a Aplicação

```bash
# Iniciar servidor de desenvolvimento
make dev
```

🎉 **Pronto!** A aplicação estará disponível em:
- 🌐 **API:** http://localhost:8000
- 📚 **Documentação:** http://localhost:8000/docs
- 🩺 **Health Check:** http://localhost:8000/health

## 🛠️ Comandos Disponíveis

```bash
# 📖 Ver todos os comandos
make help

# 🔧 Configuração e instalação
make setup          # Configuração inicial completa
make install         # Instalar dependências de produção
make install-dev     # Instalar dependências de desenvolvimento

# 🚀 Desenvolvimento
make dev            # Servidor de desenvolvimento
make run            # Servidor em modo produção

# 🧪 Testes
make test           # Executar todos os testes
make test-cov       # Testes com cobertura
make test-unit      # Apenas testes unitários
make test-integration # Apenas testes de integração

# 🔍 Qualidade de código
make lint           # Verificar qualidade (flake8 + mypy)
make format         # Formatar código (black + isort)
make format-check   # Verificar formatação

# 🧹 Limpeza
make clean          # Limpar arquivos temporários
make clean-all      # Limpar TUDO (incluindo .venv)

# 📋 Informações
make status         # Status do projeto
```

## 🧪 Executando Testes

```bash
# Todos os testes
make test

# Com relatório de cobertura
make test-cov

# Apenas unitários
make test-unit

# Apenas integração
make test-integration
```

## 🔍 Qualidade de Código

```bash
# Verificar qualidade
make lint

# Formatar código
make format

# Verificar se está bem formatado
make format-check
```

## 📦 Tecnologias Utilizadas

### Core
- **FastAPI** 0.111.x - Framework web assíncrono
- **Uvicorn** 0.29.x - Servidor ASGI
- **Pydantic** 2.7.x - Validação de dados
- **Python-jose** - JWT para autenticação

### Banco de Dados
- **Motor** 3.4.x - Driver MongoDB assíncrono
- **Redis** 5.0.x - Cache e sessões

### Desenvolvimento
- **Pytest** 8.2.x - Framework de testes
- **Black** - Formatação de código
- **isort** - Organização de imports
- **Flake8** - Linter
- **MyPy** - Verificação de tipos

## 🔄 Estrutura da API

### Health Check
- `GET /health` - Status básico da aplicação
- `GET /health/detailed` - Status detalhado com dependências

### Autenticação (Em desenvolvimento)
- `POST /auth/register` - Registro de usuário
- `POST /auth/login` - Login
- `POST /auth/logout` - Logout

### Contas Financeiras (Em desenvolvimento)
- `GET /api/v1/accounts` - Listar contas
- `POST /api/v1/accounts` - Criar conta
- `PUT /api/v1/accounts/{id}` - Atualizar conta
- `DELETE /api/v1/accounts/{id}` - Remover conta

### Transações (Em desenvolvimento)
- `GET /api/v1/transactions` - Listar transações
- `POST /api/v1/transactions` - Criar transação
- `PUT /api/v1/transactions/{id}` - Atualizar transação

## 🐳 Docker (Futuro)

```bash
# Build da imagem
make docker-build

# Executar container
make docker-run
```

## 🤝 Contribuindo

1. **Fork** o projeto
2. Crie uma **branch** para sua feature (`git checkout -b feature/MinhaFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add: MinhaFeature'`)
4. **Push** para a branch (`git push origin feature/MinhaFeature`)
5. Abra um **Pull Request**

### Padrões de Commit

```bash
# Formato
[tipo] Descrição clara e concisa

# Exemplos
[feat] Add: endpoint de criação de contas
[fix] Fix: validação de email no registro
[docs] Update: documentação da API
[test] Add: testes para autenticação
[refactor] Refactor: reorganização da estrutura
```

## 📄 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

- 📧 **Email:** dev@financeiro.com
- 🐛 **Issues:** [GitHub Issues](https://github.com/angelo/financeiro-backend/issues)
- 📖 **Documentação:** [API Docs](http://localhost:8000/docs)

---

🎯 **Status do Projeto:** Em desenvolvimento ativo
📊 **Versão:** 0.1.0  
🏗️ **Arquitetura:** Hexagonal (Ports & Adapters)  
⚡ **Framework:** FastAPI + Motor + MongoDB + Redis
# conta
