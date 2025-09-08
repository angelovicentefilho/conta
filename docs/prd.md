# **Product Requirements Document (PRD): Sistema de Controle de Contas Pessoal (MVP)**

## **1. Metas e Contexto de Fundo**

### **Metas**

1. **Criar uma plataforma centralizada para o usuário registrar e visualizar todas as suas despesas e receitas.**
2. **Oferecer uma visão clara e simples da saúde financeira do usuário através de um painel de controle.**
3. **Permitir a categorização de transações para que o usuário entenda para onde seu dinheiro está indo.**
4. **Garantir que o sistema seja intuitivo e fácil de usar, sem funcionalidades excessivamente complexas.**

### **Contexto de Fundo**

O objetivo deste projeto é desenvolver um sistema de controle de contas pessoal para solucionar problemas reais de gestão financeira. A estratégia adotada é a de um lançamento ágil através de um MVP (Minimum Viable Product), focando nas funcionalidades essenciais para validar a aceitação dos usuários e obter feedback rápido. Esta abordagem permite um desenvolvimento inicial rápido, construindo uma base sólida sobre a qual funcionalidades mais avançadas serão adicionadas em fases futuras.

### **Change Log**

| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 31/08/2025 | 1.0 | Criação inicial do PRD, definição de metas, requisitos e épicos. | Pirilampo |

## **2. Requisitos**

### **Funcionais**

1. **FR1: Autenticação de Usuário:** O sistema deve permitir que os usuários criem uma conta, façam login e logout. Deve incluir validação de e-mail, um processo para recuperação de senha e exigir senhas com critérios mínimos de segurança (ex: 8 caracteres, letras e números).
2. **FR2: Gestão de Contas:** Os usuários devem poder cadastrar, editar e excluir suas contas financeiras (ex: conta corrente, poupança, cartão de crédito). Cada conta deve ter um nome, tipo e saldo inicial. O usuário deve poder definir uma conta como 'principal' para novas transações.
3. **FR3: Registro de Transações:** Os usuários devem poder registrar manualmente receitas e despesas, especificando a conta, data, valor, descrição e uma categoria. O sistema deve suportar o registro de transações recorrentes básicas (ex: mensais).
4. **FR4: Edição de Transações:** O sistema deve permitir que transações já registradas sejam editadas ou excluídas.
5. **FR5: Gestão de Categorias:** O sistema deve fornecer uma lista de categorias padrão (ex: Alimentação, Transporte) e permitir que os usuários criem, editem e excluam suas próprias categorias personalizadas.
6. **FR6: Dashboard Principal:** Ao fazer login, o usuário deve ser apresentado a um painel que exibe o saldo total, as receitas e despesas do mês atual, e um gráfico simples (ex: pizza ou barras) mostrando a distribuição dos gastos.
7. **FR7: Relatórios Básicos:** O sistema deve ser capaz de gerar relatórios de extrato por período e um resumo de gastos por categoria.
8. **FR8: Exportação de Relatórios:** Os relatórios gerados devem ser exportáveis nos formatos PDF e CSV.
9. **FR9: Gestão de Perfil:** Os usuários devem poder visualizar e editar suas informações de perfil, incluindo preferências de moeda e fuso horário.

### **Não Funcionais**

1. **NFR1: Segurança:** A comunicação com o servidor deve ser feita exclusivamente via HTTPS. As senhas dos usuários devem ser armazenadas de forma segura utilizando um algoritmo de hash forte (ex: bcrypt).
2. **NFR2: Usabilidade:** A interface deve seguir padrões de design consistentes em todas as telas, garantindo uma experiência de usuário coesa e previsível.
3. **NFR3: Desempenho:** As consultas principais, como carregar o dashboard e gerar relatórios, devem ser concluídas em menos de 3 segundos.
4. **NFR4: Responsividade:** A interface do dashboard deve ser funcional e legível tanto em navegadores de desktop quanto em dispositivos móveis.

## **3. Suposições Técnicas**

* **Estrutura do Repositório: Polyrepo**
  * *Rationale:* Manteremos repositórios separados para o backend (API) e o futuro frontend.
* **Arquitetura do Serviço: Monolito**
  * *Rationale:* A lógica de negócio do backend será contida em uma única aplicação. Para o escopo do MVP, esta abordagem acelera o desenvolvimento.
* **Requisitos de Testes: Apenas Testes Unitários**
  * *Rationale:* O foco inicial será em garantir a qualidade das unidades de código individuais.

## **4. Épicos e Histórias de Usuário**

### **Épico 1: Fundação e Controle Financeiro Essencial**

* **Objetivo:** Construir o serviço de backend para o MVP, incluindo autenticação de usuário, gerenciamento de contas e o registro completo de transações financeiras.

#### **História 1.1: Configuração Inicial do Backend**

**Como um** desenvolvedor, **eu quero** configurar a estrutura inicial do projeto de backend, **para que** tenhamos uma base de código organizada e pronta.
**Critérios de Aceite:**

1. Um novo repositório Git deve ser criado para o backend.
2. A estrutura de pastas inicial, alinhada com a Arquitetura Hexagonal, deve ser criada.
3. As dependências principais do projeto devem ser instaladas.
4. Um arquivo de configuração de ambiente (`.env.example`) deve ser criado.
5. Um endpoint de "health check" (`GET /health`) deve retornar "OK".

#### **História 1.2: Autenticação de Usuário**

**Como um** novo usuário, **eu quero** criar uma conta segura com meu e-mail e senha, **para que** eu possa acessar o sistema com exclusividade.
**Critérios de Aceite:**

1. Deve ser possível criar uma conta com nome, e-mail e senha.
2. A senha deve atender aos critérios mínimos de segurança.
3. O sistema deve validar se o e-mail já está em uso.
4. Após o registro, o usuário deve conseguir fazer login.
5. Deve haver uma função de "Esqueci minha senha".

#### **História 1.3: Gestão de Contas Financeiras**

**Como um** usuário, **eu quero** cadastrar e gerenciar minhas diferentes contas, **para que** eu tenha uma visão centralizada de onde meu dinheiro está.
**Critérios de Aceite:**

1. O usuário pode adicionar uma nova conta (nome, tipo, saldo inicial).
2. O usuário pode visualizar uma lista de todas as suas contas.
3. O usuário pode editar ou excluir uma conta.
4. O usuário pode definir uma conta como "principal".

#### **História 1.4: Registro de Transações**

**Como um** usuário, **eu quero** registrar todas as minhas transações financeiras, **para que** o sistema reflita minha situação financeira real.
**Critérios de Aceite:**

1. O usuário pode registrar uma "Receita" ou "Despesa".
2. O formulário deve incluir data, descrição, valor, conta e categoria.
3. A conta "principal" deve ser pré-selecionada.
4. O usuário pode marcar uma transação como recorrente (mensal).
5. O usuário pode editar ou excluir uma transação.

#### **História 1.5: Visualização Financeira no Dashboard**

**Como um** usuário, **eu quero** ver um resumo visual da minha saúde financeira, **para que** eu possa entender rapidamente minha situação.
**Critérios de Aceite:**

1. O dashboard deve exibir o saldo consolidado de todas as contas.
2. O dashboard deve mostrar o total de receitas e despesas do mês.
3. Um gráfico deve mostrar a distribuição de despesas por categoria.

#### **História 1.6: Geração de Relatórios Básicos**

**Como um** usuário, **eu quero** gerar relatórios simples, **para que** eu possa analisar meus gastos com mais detalhes.
**Critérios de Aceite:**

1. O usuário pode gerar um extrato por período de datas.
2. O usuário pode gerar um relatório de despesas por categoria por período.
3. Os relatórios podem ser exportados para PDF e CSV.
