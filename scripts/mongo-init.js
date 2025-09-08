// Script de inicialização do MongoDB para o Sistema Financeiro
// Este script é executado automaticamente durante a criação do container

print("🚀 Iniciando configuração do banco de dados 'financeiro'...");

// Conecta ao banco de dados
db = db.getSiblingDB('financeiro');

// Cria usuário específico para a aplicação
db.createUser({
  user: 'financeiro_app',
  pwd: 'financeiro123',
  roles: [
    {
      role: 'readWrite',
      db: 'financeiro'
    }
  ]
});

// Cria coleções iniciais com validação
print("📊 Criando coleções com validação...");

// Coleção de usuários
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "email", "password_hash"],
      properties: {
        name: { bsonType: "string" },
        email: { bsonType: "string" },
        password_hash: { bsonType: "string" },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" },
        is_active: { bsonType: "bool" }
      }
    }
  }
});

// Coleção de contas
db.createCollection("accounts", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "name", "account_type", "balance"],
      properties: {
        user_id: { bsonType: "string" },
        name: { bsonType: "string" },
        account_type: { bsonType: "string" },
        balance: { bsonType: "decimal" },
        is_primary: { bsonType: "bool" },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" },
        is_active: { bsonType: "bool" }
      }
    }
  }
});

// Coleção de categorias
db.createCollection("categories", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "name", "category_type"],
      properties: {
        user_id: { bsonType: "string" },
        name: { bsonType: "string" },
        category_type: { bsonType: "string" },
        color: { bsonType: "string" },
        icon: { bsonType: "string" },
        is_system: { bsonType: "bool" },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" },
        is_active: { bsonType: "bool" }
      }
    }
  }
});

// Coleção de transações
db.createCollection("transactions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "account_id", "category_id", "type", "amount", "date"],
      properties: {
        user_id: { bsonType: "string" },
        account_id: { bsonType: "string" },
        category_id: { bsonType: "string" },
        type: { bsonType: "string" },
        amount: { bsonType: "decimal" },
        description: { bsonType: "string" },
        date: { bsonType: "date" },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" }
      }
    }
  }
});

// Cria índices para performance
print("🔍 Criando índices para performance...");

// Índices para usuários
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "is_active": 1 });

// Índices para contas
db.accounts.createIndex({ "user_id": 1 });
db.accounts.createIndex({ "user_id": 1, "is_primary": 1 });
db.accounts.createIndex({ "is_active": 1 });

// Índices para categorias
db.categories.createIndex({ "user_id": 1 });
db.categories.createIndex({ "user_id": 1, "category_type": 1 });
db.categories.createIndex({ "is_system": 1 });

// Índices para transações
db.transactions.createIndex({ "user_id": 1 });
db.transactions.createIndex({ "account_id": 1 });
db.transactions.createIndex({ "category_id": 1 });
db.transactions.createIndex({ "user_id": 1, "date": -1 });
db.transactions.createIndex({ "type": 1 });
db.transactions.createIndex({ "date": -1 });

print("✅ Configuração do banco de dados concluída com sucesso!");
print("📋 Resumo:");
print("   - Usuário da aplicação: financeiro_app");
print("   - Banco de dados: financeiro");
print("   - Coleções criadas: users, accounts, categories, transactions");
print("   - Índices otimizados criados");
