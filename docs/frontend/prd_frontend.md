# Product Requirements Document (PRD) - Controle Fácil

## 1. Visão Geral

**Controle Fácil** é uma aplicação web de finanças pessoais projetada para ajudar os usuários a gerenciar suas finanças de forma intuitiva e inteligente. A plataforma permite que os usuários consolidem suas contas, registrem transações, criem orçamentos, definam metas financeiras e obtenham insights valiosos por meio de ferramentas de Inteligência Artificial.

Este documento detalha os requisitos para o sistema de backend que suportará as funcionalidades da aplicação frontend.

## 2. Requisitos Funcionais

### 2.1. Autenticação de Usuário

**Objetivo:** Fornecer um sistema de autenticação seguro para registrar e autenticar usuários.

**Endpoints da API:**

* `POST /api/auth/register`
  * **Descrição:** Registra um novo usuário.
  * **Payload (Corpo):** `{ "name": "string", "email": "string", "password": "string" }`
  * **Resposta de Sucesso (201):** `{ "userId": "string", "token": "JWT_string" }`
  * **Respostas de Erro:** `400` (Dados inválidos), `409` (Email já existe).

* `POST /api/auth/login`
  * **Descrição:** Autentica um usuário existente.
  * **Payload (Corpo):** `{ "email": "string", "password": "string" }`
  * **Resposta de Sucesso (200):** `{ "userId": "string", "token": "JWT_string" }`
  * **Respostas de Erro:** `401` (Credenciais inválidas).

* `POST /api/auth/recover`
  * **Descrição:** Inicia o processo de recuperação de senha.
  * **Payload (Corpo):** `{ "email": "string" }`
  * **Resposta de Sucesso (200):** `{ "message": "Password recovery email sent." }`

### 2.2. Gerenciamento de Contas Financeiras

**Objetivo:** Permitir que os usuários gerenciem suas contas financeiras (corrente, poupança, cartão de crédito).

**Endpoints da API:**

* `GET /api/accounts`
  * **Descrição:** Retorna todas as contas do usuário autenticado.
  * **Resposta de Sucesso (200):** `[ { "id": "string", "name": "string", "type": "checking" | "savings" | "credit_card", "initialBalance": number, "currentBalance": number, "isPrincipal": boolean } ]`

* `POST /api/accounts`
  * **Descrição:** Cria uma nova conta.
  * **Payload (Corpo):** `{ "name": "string", "type": "string", "initialBalance": number, "isPrincipal": boolean }`
  * **Resposta de Sucesso (201):** `{ "id": "string", ... }` (O objeto da conta criada).
  * **Lógica de Negócio:** `currentBalance` deve ser inicializado com o valor de `initialBalance`.

* `PUT /api/accounts/{accountId}`
  * **Descrição:** Atualiza uma conta existente.
  * **Payload (Corpo):** `{ "name": "string", "isPrincipal": boolean }`
  * **Resposta de Sucesso (200):** `{ "id": "string", ... }` (O objeto da conta atualizada).

* `DELETE /api/accounts/{accountId}`
  * **Descrição:** Exclui uma conta.
  * **Resposta de Sucesso (204):** Sem conteúdo.

### 2.3. Gerenciamento de Transações

**Objetivo:** Permitir o registro, visualização, edição e exclusão de transações de receita e despesa.

**Endpoints da API:**

* `GET /api/transactions`
  * **Descrição:** Retorna as transações do usuário, com filtros.
  * **Parâmetros de Query:** `?month=YYYY-MM` (obrigatório), `?categories=cat1,cat2` (opcional).
  * **Resposta de Sucesso (200):** `[ { "id": "string", "accountId": "string", "type": "income" | "expense", "date": "ISO_string", "amount": number, "description": "string", "category": "string" } ]`

* `POST /api/transactions`
  * **Descrição:** Adiciona uma nova transação.
  * **Payload (Corpo):** Objeto da transação sem o `id`.
  * **Resposta de Sucesso (201):** O objeto da transação criada.
  * **Lógica de Negócio:** Ao adicionar uma transação, o `currentBalance` da conta (`accountId`) associada deve ser atualizado.

* `PUT /api/transactions/{transactionId}`
  * **Descrição:** Atualiza uma transação.
  * **Payload (Corpo):** Objeto parcial ou completo da transação.
  * **Resposta de Sucesso (200):** O objeto da transação atualizada.
  * **Lógica de Negócio:** Reverter o efeito da transação original no saldo da conta e aplicar o novo.

* `DELETE /api/transactions/{transactionId}`
  * **Descrição:** Exclui uma transação.
  * **Resposta de Sucesso (204):** Sem conteúdo.
  * **Lógica de Negócio:** Reverter o efeito da transação no saldo da conta associada.

### 2.4. Gerenciamento de Metas

**Objetivo:** Permitir a criação e o acompanhamento de metas financeiras.

**Endpoints da API:**

* `GET /api/goals`
  * **Descrição:** Retorna todas as metas do usuário.
  * **Resposta de Sucesso (200):** `[ { "id": "string", "name": "string", "description": "string", "targetAmount": number, "currentAmount": number, "deadline": "ISO_string" } ]`

* `POST /api/goals`
  * **Descrição:** Cria uma nova meta. `currentAmount` deve ser 0.
  * **Payload (Corpo):** Objeto da meta sem `id` e `currentAmount`.
  * **Resposta de Sucesso (201):** O objeto da meta criada.

* `POST /api/goals/{goalId}/contribute`
  * **Descrição:** Adiciona uma contribuição a uma meta.
  * **Payload (Corpo):** `{ "amount": number }`
  * **Resposta de Sucesso (200):** O objeto da meta atualizada.
  * **Lógica de Negócio:** Incrementar `currentAmount` no objeto da meta.

* `PUT /api/goals/{goalId}`
  * **Descrição:** Atualiza os detalhes de uma meta.
  * **Resposta de Sucesso (200):** O objeto da meta atualizada.

* `DELETE /api/goals/{goalId}`
  * **Descrição:** Exclui uma meta.
  * **Resposta de Sucesso (204):** Sem conteúdo.

### 2.5. Gerenciamento de Orçamentos

**Objetivo:** Permitir que os usuários definam orçamentos mensais por categoria e acompanhem seus gastos.

**Endpoints da API:**

* `GET /api/budgets`
  * **Descrição:** Retorna os orçamentos para um determinado mês.
  * **Parâmetros de Query:** `?month=YYYY-MM` (obrigatório).
  * **Resposta de Sucesso (200):** `[ { "id": "string", "categoryId": "string", "amount": number, "month": "YYYY-MM" } ]`

* `POST /api/budgets`
  * **Descrição:** Cria ou atualiza um orçamento para uma categoria em um mês.
  * **Payload (Corpo):** `{ "categoryId": "string", "amount": number, "month": "YYYY-MM" }`
  * **Resposta de Sucesso (200 ou 201):** O objeto do orçamento criado/atualizado.

### 2.6. Integrações com IA (Genkit Flows)

**Objetivo:** Fornecer endpoints que atuem como wrappers para os fluxos de IA definidos.

* `POST /api/ai/categorize-transaction`
  * **Descrição:** Wrapper para o fluxo `categorizeTransaction`.
  * **Payload:** `CategorizeTransactionInput`
  * **Resposta:** `CategorizeTransactionOutput`

* `POST /api/ai/analyze-expenses`
  * **Descrição:** Wrapper para o fluxo `analyzeExpenses`.
  * **Payload:** `ExpenseAnalysisInput`
  * **Resposta:** `ExpenseAnalysisOutput`

* `POST /api/ai/create-goal`
  * **Descrição:** Wrapper para o fluxo `createGoalFromPrompt`.
  * **Payload:** `CreateGoalFromPromptInput`
  * **Resposta:** `CreateGoalFromPromptOutput`

* `POST /api/ai/budget-recommendations`
  * **Descrição:** Wrapper para o fluxo `getBudgetRecommendations`.
  * **Payload:** `BudgetRecommendationInput`
  * **Resposta:** `BudgetRecommendationOutput`

### 2.7. Gerenciamento de Perfil

**Objetivo:** Permitir que o usuário visualize e atualize suas informações de perfil.

* `GET /api/profile`
  * **Descrição:** Retorna os dados do perfil do usuário.
  * **Resposta (200):** `{ "name": "string", "email": "string", "avatarUrl": "string", "preferences": { "currency": "BRL" | "USD" | "EUR", "timezone": "string" } }`

* `PUT /api/profile`
  * **Descrição:** Atualiza os dados do perfil.
  * **Payload (Corpo):** Objeto parcial do perfil.
  * **Resposta (200):** O objeto do perfil atualizado.

* `POST /api/profile/avatar`
  * **Descrição:** Faz upload de uma nova imagem de avatar.
  * **Payload (Corpo):** `FormData` com o arquivo da imagem.
  * **Resposta (200):** `{ "avatarUrl": "string" }`

### 2.8. Categorias

**Objetivo:** Fornecer a lista de categorias disponíveis no sistema.

* `GET /api/categories`
  * **Descrição:** Retorna a lista de todas as categorias.
  * **Resposta (200):** `[ { "id": "string", "name": "string", "type": "income" | "expense" } ]`

## 3. Modelos de Dados (Schema do Banco de Dados)

* **User:**
  * `id` (PK)
  * `name`
  * `email` (Unique)
  * `passwordHash`
  * `avatarUrl`
  * `currencyPreference`
  * `timezonePreference`

* **Account:**
  * `id` (PK)
  * `userId` (FK to User)
  * `name`
  * `type`
  * `initialBalance`
  * `currentBalance`
  * `isPrincipal`

* **Transaction:**
  * `id` (PK)
  * `userId` (FK to User)
  * `accountId` (FK to Account)
  * `categoryId` (FK to Category)
  * `type`
  * `date`
  * `amount`
  * `description`

* **Category:** (Pode ser uma tabela pré-populada)
  * `id` (PK)
  * `name` (Unique)
  * `type`

* **Goal:**
  * `id` (PK)
  * `userId` (FK to User)
  * `name`
  * `description`
  * `targetAmount`
  * `currentAmount`
  * `deadline`

* **Budget:**
  * `id` (PK)
  * `userId` (FK to User)
  * `categoryId` (FK to Category)
  * `amount`
  * `month` (Formato YYYY-MM)
  * Índice único em (`userId`, `categoryId`, `month`).
