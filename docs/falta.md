# Documento de Funcionalidades Pendentes - Backend (MongoDB)

Este documento descreve os endpoints da API e os modelos de dados que precisam ser desenvolvidos no backend para suportar as funcionalidades de **Metas (Goals)** e **Orçamentos (Budgets)**.

O backend utiliza **MongoDB**, portanto os modelos são apresentados como documentos JSON.

## 1. Gerenciamento de Metas (Goals)

**Objetivo:** Permitir que os usuários criem, visualizem, atualizem e excluam metas financeiras, além de registrarem contribuições para elas.

### 1.1. Modelo de Dados - Coleção `goals`

```json
{
  "_id": "ObjectId('...')",
  "userId": "ObjectId('...')", // FK para a coleção 'users'
  "name": "Viagem para a Europa",
  "description": "Economizar para uma viagem de 15 dias pela Itália e França.",
  "targetAmount": "Decimal128('25000.00')",
  "currentAmount": "Decimal128('7500.00')",
  "deadline": "ISODate('2025-12-31T23:59:59Z')",
  "createdAt": "ISODate('...')",
  "updatedAt": "ISODate('...')"
}
```

### 1.2. Endpoints da API para Metas

**Tag da API:** `goals`

---

#### 1.2.1. Listar Metas

-   **Endpoint:** `GET /api/v1/goals/`
-   **Sumário:** Listar todas as metas do usuário.
-   **Descrição:** Retorna uma lista de todas as metas financeiras pertencentes ao usuário autenticado.
-   **Segurança:** Requer token JWT.
-   **Resposta de Sucesso (200 OK):**
    ```json
    [
      {
        "id": "60d5ecb4b392a0d1a4e2b0f3",
        "name": "Viagem para a Europa",
        "description": "Economizar para uma viagem de 15 dias pela Itália e França.",
        "targetAmount": "25000.00",
        "currentAmount": "7500.00",
        "deadline": "2025-12-31T23:59:59Z",
        "createdAt": "2024-01-15T10:00:00Z"
      }
    ]
    ```

---

#### 1.2.2. Criar Meta

-   **Endpoint:** `POST /api/v1/goals/`
-   **Sumário:** Criar uma nova meta.
-   **Descrição:** Cria uma nova meta financeira para o usuário. `currentAmount` é inicializado como 0.
-   **Segurança:** Requer token JWT.
-   **Payload (Corpo):**
    ```json
    {
      "name": "Comprar um MacBook Pro",
      "description": "Modelo M3 Pro, 1TB",
      "targetAmount": "18000.00",
      "deadline": "2025-12-31T23:59:59Z"
    }
    ```
-   **Resposta de Sucesso (201 Created):**
    ```json
    {
      "id": "60d5ecb4b392a0d1a4e2b0f4",
      "name": "Comprar um MacBook Pro",
      "description": "Modelo M3 Pro, 1TB",
      "targetAmount": "18000.00",
      "currentAmount": "0.00",
      "deadline": "2025-12-31T23:59:59Z",
      "createdAt": "2024-08-01T12:00:00Z"
    }
    ```
-   **Resposta de Erro (400 Bad Request):**
    ```json
    { "detail": "O valor alvo (targetAmount) deve ser maior que zero." }
    ```

---

#### 1.2.3. Atualizar Meta

-   **Endpoint:** `PUT /api/v1/goals/{goal_id}`
-   **Sumário:** Atualizar os detalhes de uma meta.
-   **Descrição:** Atualiza nome, descrição, valor alvo ou prazo. Não deve ser usado para contribuições.
-   **Segurança:** Requer token JWT.
-   **Payload (Corpo):** (Campos são opcionais)
    ```json
    {
      "name": "Viagem para o Japão",
      "targetAmount": "30000.00"
    }
    ```
-   **Resposta de Sucesso (200 OK):** Objeto da meta atualizado.
-   **Resposta de Erro (404 Not Found):**
    ```json
    { "detail": "Meta com id '...' não encontrada." }
    ```

---

#### 1.2.4. Excluir Meta

-   **Endpoint:** `DELETE /api/v1/goals/{goal_id}`
-   **Sumário:** Excluir uma meta.
-   **Segurança:** Requer token JWT.
-   **Resposta de Sucesso (204 No Content):** Sem conteúdo.
-   **Resposta de Erro (404 Not Found):**
    ```json
    { "detail": "Meta com id '...' não encontrada." }
    ```

---

#### 1.2.5. Adicionar Contribuição

-   **Endpoint:** `POST /api/v1/goals/{goal_id}/contribute`
-   **Sumário:** Adicionar uma contribuição a uma meta.
-   **Descrição:** Adiciona um valor ao `currentAmount`.
-   **Segurança:** Requer token JWT.
-   **Payload (Corpo):**
    ```json
    { "amount": "500.00" }
    ```
-   **Resposta de Sucesso (200 OK):** Objeto da meta com `currentAmount` atualizado.
-   **Resposta de Erro (400 Bad Request):**
    ```json
    { "detail": "O valor da contribuição deve ser positivo." }
    ```
-   **Resposta de Erro (404 Not Found):**
    ```json
    { "detail": "Meta com id '...' não encontrada." }
    ```

## 2. Gerenciamento de Orçamentos (Budgets)

**Objetivo:** Permitir que usuários definam orçamentos mensais por categoria.

### 2.1. Modelo de Dados - Coleção `budgets`

```json
{
  "_id": "ObjectId('...')",
  "userId": "ObjectId('...')",    // FK para 'users'
  "categoryId": "ObjectId('...')", // FK para 'categories'
  "amount": "Decimal128('800.00')",
  "month": "2024-08-01T00:00:00Z", // Armazenar sempre como o primeiro dia do mês
  "createdAt": "ISODate('...')",
  "updatedAt": "ISODate('...')"
}
```
**Índice:** Um índice único deve ser criado em `{ userId: 1, categoryId: 1, month: 1 }` para garantir um orçamento por categoria/mês por usuário.

### 2.2. Endpoints da API para Orçamentos

**Tag da API:** `budgets`

---

#### 2.2.1. Listar Orçamentos de um Mês

-   **Endpoint:** `GET /api/v1/budgets/`
-   **Sumário:** Listar orçamentos de um mês.
-   **Descrição:** Retorna todos os orçamentos definidos para um mês específico.
-   **Segurança:** Requer token JWT.
-   **Parâmetros de Query:** `month=YYYY-MM` (obrigatório).
-   **Resposta de Sucesso (200 OK):**
    ```json
    [
      {
        "id": "60d5ecb4b392a0d1a4e2b0f5",
        "categoryId": "cat1_id_from_db",
        "categoryName": "Alimentação",
        "amount": "800.00",
        "month": "2024-08",
        "createdAt": "2024-07-28T10:00:00Z"
      }
    ]
    ```

---

#### 2.2.2. Criar ou Atualizar Orçamento

-   **Endpoint:** `POST /api/v1/budgets/`
-   **Sumário:** Criar ou atualizar um orçamento (Upsert).
-   **Descrição:** Cria um novo orçamento. Se já existir um para a mesma categoria e mês, atualiza o valor.
-   **Segurança:** Requer token JWT.
-   **Payload (Corpo):**
    ```json
    {
      "categoryId": "cat1_id_from_db",
      "amount": "850.50",
      "month": "2024-09"
    }
    ```
-   **Resposta de Sucesso (200 OK para update, 201 Created para create):**
    ```json
    {
      "id": "60d5ecb4b392a0d1a4e2b0f6",
      "categoryId": "cat1_id_from_db",
      "categoryName": "Alimentação",
      "amount": "850.50",
      "month": "2024-09",
      "createdAt": "2024-08-01T15:00:00Z"
    }
    ```
-   **Resposta de Erro (404 Not Found):**
    ```json
    { "detail": "Categoria com id '...' não encontrada." }
    ```

---

#### 2.2.3. Excluir Orçamento

-   **Endpoint:** `DELETE /api/v1/budgets/{budget_id}`
-   **Sumário:** Excluir um orçamento.
-   **Segurança:** Requer token JWT.
-   **Resposta de Sucesso (204 No Content):** Sem conteúdo.
-   **Resposta de Erro (404 Not Found):**
    ```json
    { "detail": "Orçamento com id '...' não encontrado." }
    ```
