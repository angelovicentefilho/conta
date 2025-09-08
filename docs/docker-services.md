# 🐳 Guia dos Serviços Docker

Este projeto usa MongoDB e Redis como serviços externos via Docker Compose.

## 🚀 Comandos Rápidos

### Todos os Serviços
```bash
make services-up      # Inicia MongoDB + Redis
make services-down    # Para MongoDB + Redis  
make services-status  # Status dos serviços
make services-logs    # Logs dos serviços
```

### MongoDB (Banco de Dados)
```bash
make mongo-up         # Inicia apenas MongoDB
make mongo-down       # Para apenas MongoDB
make mongo-logs       # Logs do MongoDB
```

### Redis (Cache)
```bash
make redis-up         # Inicia apenas Redis
make redis-down       # Para apenas Redis
make redis-logs       # Logs do Redis
```

## 📊 Informações de Conexão

### MongoDB
- **URL**: `mongodb://localhost:27017`
- **Admin**: `admin` / `admin123`
- **App User**: `financeiro_app` / `financeiro123`
- **Database**: `financeiro`

### Redis
- **URL**: `redis://localhost:6379`
- **Password**: `redis123`
- **Database**: `0` (produção), `1` (teste)

## 🔧 Configuração Local

1. **Inicie os serviços**:
   ```bash
   make services-up
   ```

2. **Copie o arquivo de ambiente**:
   ```bash
   cp .env.example .env
   ```

3. **Inicie a aplicação**:
   ```bash
   make dev
   ```

## 🛠️ Gerenciamento

### Volumes Persistentes
- `mongodb_data`: Dados do MongoDB
- `redis_data`: Dados do Redis

### Rede
- `financeiro_network`: Rede interna dos serviços

### Health Checks
- MongoDB: Verifica conexão com `mongosh`
- Redis: Verifica comando `ping`

## 🔍 Troubleshooting

### MongoDB não inicia
```bash
docker-compose logs mongodb
```

### Redis não conecta
```bash
docker-compose logs redis
```

### Reiniciar serviços
```bash
make services-down
make services-up
```

### Limpar volumes (⚠️ perde dados)
```bash
docker-compose down -v
```
