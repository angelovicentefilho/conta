from datetime import datetime
from typing import Dict, Optional, List
import uuid
from uuid import UUID

from app.core.domain.user import User, UserCreate, PasswordResetToken
from app.core.ports.auth import (
    UserRepositoryPort, PasswordResetRepositoryPort
)
from app.core.domain.account import Account
from app.core.ports.account import AccountRepository
from app.core.domain.transaction import Transaction, Category, TransactionType
from app.core.ports.transaction import (
    TransactionRepository, CategoryRepository
)
from app.core.domain.goal import Goal
from app.core.ports.goal import GoalRepository
from app.core.domain.budget import Budget
from app.core.ports.budget import BudgetRepository
from app.core.domain.exceptions import (
    AccountAlreadyExistsError,
    AccountNotFoundError,
    CategoryNotFoundError,
    CannotDeleteSystemCategoryError,
    CategoryInUseError,
    GoalNotFoundError,
)


class InMemoryUserRepository(UserRepositoryPort):
    """Implementação in-memory do repositório de usuários."""

    def __init__(self) -> None:
        self._users: Dict[str, User] = {}
        self._users_by_email: Dict[str, str] = {}

    async def create_user(self, user_data: UserCreate) -> User:
        """Cria um novo usuário."""
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        user = User(
            id=user_id,
            name=user_data.name,
            email=user_data.email,
            password_hash=user_data.password,  # Já vem hasheada do service
            created_at=now,
            updated_at=now,
            is_active=True
        )
        
        self._users[user_id] = user
        self._users_by_email[user_data.email] = user_id
        
        return user

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Busca usuário por ID."""
        return self._users.get(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por e-mail."""
        user_id = self._users_by_email.get(email)
        if user_id:
            return self._users.get(user_id)
        return None

    async def update_user_password(
        self, user_id: str, password_hash: str
    ) -> bool:
        """Atualiza a senha do usuário."""
        user = self._users.get(user_id)
        if user:
            # Cria nova instância com senha atualizada
            updated_user = User(
                id=user.id,
                name=user.name,
                email=user.email,
                password_hash=password_hash,
                created_at=user.created_at,
                updated_at=datetime.utcnow(),
                is_active=user.is_active
            )
            self._users[user_id] = updated_user
            return True
        return False

    async def deactivate_user(self, user_id: str) -> bool:
        """Desativa um usuário."""
        user = self._users.get(user_id)
        if user:
            # Cria nova instância desativada
            deactivated_user = User(
                id=user.id,
                name=user.name,
                email=user.email,
                password_hash=user.password_hash,
                created_at=user.created_at,
                updated_at=datetime.utcnow(),
                is_active=False
            )
            self._users[user_id] = deactivated_user
            return True
        return False
    
    def clear(self) -> None:
        """Limpa todos os dados do repositório."""
        self._users.clear()
        self._users_by_email.clear()


class InMemoryPasswordResetRepository(PasswordResetRepositoryPort):
    """Implementação in-memory do repositório de tokens de reset."""

    def __init__(self) -> None:
        self._tokens: Dict[str, PasswordResetToken] = {}

    async def create_reset_token(
        self, user_id: str, token_hash: str, expires_at: datetime
    ) -> PasswordResetToken:
        """Cria um token de reset de senha."""
        token_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        reset_token = PasswordResetToken(
            id=token_id,
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            used=False,
            created_at=now
        )
        
        self._tokens[token_id] = reset_token
        return reset_token

    async def get_valid_reset_token(
        self, token_hash: str
    ) -> Optional[PasswordResetToken]:
        """Busca token válido de reset (não usado e não expirado)."""
        now = datetime.utcnow()
        
        for token in self._tokens.values():
            if (token.token_hash == token_hash and
                    not token.used and
                    token.expires_at > now):
                return token
        
        return None

    async def mark_token_as_used(self, token_id: str) -> bool:
        """Marca um token como usado."""
        token = self._tokens.get(token_id)
        if token:
            # Cria nova instância marcada como usada
            used_token = PasswordResetToken(
                id=token.id,
                user_id=token.user_id,
                token_hash=token.token_hash,
                expires_at=token.expires_at,
                used=True,
                created_at=token.created_at
            )
            self._tokens[token_id] = used_token
            return True
        return False

    async def cleanup_expired_tokens(self) -> int:
        """Remove tokens expirados. Retorna quantidade removida."""
        now = datetime.utcnow()
        expired_ids = [
            token_id for token_id, token in self._tokens.items()
            if token.expires_at <= now
        ]
        
        for token_id in expired_ids:
            del self._tokens[token_id]
        
        return len(expired_ids)
    
    def clear(self) -> None:
        """Limpa todos os dados do repositório."""
        self._tokens.clear()


class InMemoryAccountRepository(AccountRepository):
    """Implementação in-memory do repositório de contas."""
    
    def __init__(self) -> None:
        self._accounts: Dict[str, Account] = {}
        self._accounts_by_user: Dict[str, List[str]] = {}
    
    async def create(self, account: Account) -> Account:
        """Cria uma nova conta no repositório."""
        # Verificar se já existe conta com mesmo nome para o usuário
        existing = await self.get_by_name_and_user(
            account.name, account.user_id
        )
        if existing:
            raise AccountAlreadyExistsError(account.name, str(account.user_id))
        
        # Armazenar conta
        account_id = str(account.id)
        user_id = str(account.user_id)
        
        self._accounts[account_id] = account
        
        if user_id not in self._accounts_by_user:
            self._accounts_by_user[user_id] = []
        self._accounts_by_user[user_id].append(account_id)
        
        return account
    
    async def get_by_id(
        self, account_id: UUID, user_id: UUID
    ) -> Optional[Account]:
        """Busca conta por ID validando propriedade."""
        account = self._accounts.get(str(account_id))
        if account and account.user_id == user_id and account.is_active:
            return account
        return None
    
    async def get_by_user_id(self, user_id: UUID) -> List[Account]:
        """Lista contas ativas do usuário ordenadas."""
        user_id_str = str(user_id)
        account_ids = self._accounts_by_user.get(user_id_str, [])
        
        accounts = []
        for account_id in account_ids:
            account = self._accounts.get(account_id)
            if account and account.is_active:
                accounts.append(account)
        
        # Ordenar: principal primeiro, depois alfabética
        accounts.sort(key=lambda a: (not a.is_primary, a.name.lower()))
        return accounts
    
    async def get_by_name_and_user(
        self, name: str, user_id: UUID
    ) -> Optional[Account]:
        """Busca conta por nome e usuário."""
        accounts = await self.get_by_user_id(user_id)
        for account in accounts:
            if account.name.lower() == name.lower():
                return account
        return None
    
    async def get_primary_account(self, user_id: UUID) -> Optional[Account]:
        """Busca conta principal do usuário."""
        accounts = await self.get_by_user_id(user_id)
        for account in accounts:
            if account.is_primary:
                return account
        return None
    
    async def update(self, account: Account) -> Account:
        """Atualiza conta existente."""
        account_id = str(account.id)
        if account_id not in self._accounts:
            raise AccountNotFoundError(account_id)
        
        # Atualizar timestamp
        account.updated_at = datetime.utcnow()
        self._accounts[account_id] = account
        return account
    
    async def delete(self, account_id: UUID, user_id: UUID) -> bool:
        """Remove conta (soft delete)."""
        account_to_delete = await self.get_by_id(account_id, user_id)
        if not account_to_delete:
            raise AccountNotFoundError(str(account_id), str(user_id))
        
        # Soft delete
        account_to_delete.deactivate()
        await self.update(account_to_delete)
        return True
    
    async def set_primary_account(
        self, account_id: UUID, user_id: UUID
    ) -> None:
        """Define conta como principal."""
        # Remover status principal de todas as contas
        accounts = await self.get_by_user_id(user_id)
        for account in accounts:
            if account.is_primary:
                account.remove_primary_status()
                await self.update(account)
        
        # Definir nova conta principal
        account_to_set = await self.get_by_id(account_id, user_id)
        if not account_to_set:
            raise AccountNotFoundError(str(account_id))
        
        account_to_set.set_as_primary()
        await self.update(account_to_set)
    
    async def count_user_accounts(self, user_id: UUID) -> int:
        """Conta contas ativas do usuário."""
        accounts = await self.get_by_user_id(user_id)
        return len(accounts)
    
    def clear(self) -> None:
        """Limpa todos os dados do repositório."""
        self._accounts.clear()
        self._accounts_by_user.clear()


class InMemoryTransactionRepository(TransactionRepository):
    """Implementação in-memory do repositório de transações."""
    
    def __init__(self) -> None:
        self._transactions: Dict[str, Transaction] = {}
        self._transactions_by_user: Dict[str, List[str]] = {}
    
    async def create(self, transaction: Transaction) -> Transaction:
        """Cria uma nova transação no repositório."""
        transaction_id = str(transaction.id)
        user_id = str(transaction.user_id)
        
        self._transactions[transaction_id] = transaction
        
        if user_id not in self._transactions_by_user:
            self._transactions_by_user[user_id] = []
        self._transactions_by_user[user_id].append(transaction_id)
        
        return transaction
    
    async def get_by_id(
        self, transaction_id: UUID, user_id: UUID
    ) -> Optional[Transaction]:
        """Busca transação por ID validando propriedade."""
        transaction = self._transactions.get(str(transaction_id))
        if (transaction and
                transaction.user_id == user_id and
                transaction.is_active):
            return transaction
        return None
    
    async def get_by_user_id(
        self,
        user_id: UUID,
        account_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        transaction_type: Optional[TransactionType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Transaction]:
        """Lista transações do usuário com filtros opcionais."""
        user_id_str = str(user_id)
        transaction_ids = self._transactions_by_user.get(user_id_str, [])
        
        transactions = []
        for tx_id in transaction_ids:
            transaction = self._transactions.get(tx_id)
            if not transaction or not transaction.is_active:
                continue
            
            # Aplicar filtros
            if account_id and transaction.account_id != account_id:
                continue
            if category_id and transaction.category_id != category_id:
                continue
            if transaction_type and transaction.type != transaction_type:
                continue
            if start_date and transaction.date < start_date:
                continue
            if end_date and transaction.date > end_date:
                continue
            
            transactions.append(transaction)
        
        # Ordenar por data (mais recentes primeiro)
        transactions.sort(key=lambda t: t.date, reverse=True)
        
        # Aplicar paginação
        return transactions[offset:offset + limit]
    
    async def update(self, transaction: Transaction) -> Transaction:
        """Atualiza uma transação existente."""
        transaction_id = str(transaction.id)
        transaction.updated_at = datetime.utcnow()
        self._transactions[transaction_id] = transaction
        return transaction
    
    async def delete(self, transaction_id: UUID, user_id: UUID) -> bool:
        """Remove transação (soft delete)."""
        transaction = await self.get_by_id(transaction_id, user_id)
        if transaction:
            transaction.deactivate()
            await self.update(transaction)
            return True
        return False
    
    async def count_by_user_id(self, user_id: UUID) -> int:
        """Conta total de transações ativas do usuário."""
        transactions = await self.get_by_user_id(user_id)
        return len(transactions)
    
    async def count_by_category_id(self, category_id: UUID) -> int:
        """Conta transações que usam uma categoria."""
        count = 0
        for transaction in self._transactions.values():
            if (transaction.category_id == category_id and
                    transaction.is_active):
                count += 1
        return count
    
    async def get_balance_by_account(
        self, account_id: UUID, user_id: UUID
    ) -> float:
        """Calcula saldo atual de uma conta baseado nas transações."""
        balance = 0.0
        
        for transaction in self._transactions.values():
            if (transaction.account_id == account_id and
                    transaction.user_id == user_id and
                    transaction.is_active):
                
                if transaction.type == TransactionType.INCOME:
                    balance += float(transaction.amount)
                else:  # EXPENSE
                    balance -= float(transaction.amount)
        
        return balance
    
    async def get_by_user_and_period(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> List[Transaction]:
        """Busca transações do usuário em um período específico."""
        return await self.get_by_user_id(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=1000  # Limite alto para pegar todas do período
        )
    
    async def get_recent_by_user(
        self, user_id: UUID, limit: int = 10
    ) -> List[Transaction]:
        """Busca as transações mais recentes do usuário."""
        return await self.get_by_user_id(
            user_id=user_id,
            limit=limit
        )
    
    def clear(self) -> None:
        """Limpa todos os dados do repositório."""
        self._transactions.clear()
        self._transactions_by_user.clear()


class InMemoryCategoryRepository(CategoryRepository):
    """Implementação in-memory do repositório de categorias."""
    
    def __init__(self) -> None:
        self._categories: Dict[str, Category] = {}
        self._categories_by_user: Dict[str, List[str]] = {}
        self._system_categories_initialized = False
    
    async def create(self, category: Category) -> Category:
        """Cria uma nova categoria."""
        category_id = str(category.id)
        user_id_str = str(category.user_id) if category.user_id else "system"
        
        self._categories[category_id] = category
        
        if user_id_str not in self._categories_by_user:
            self._categories_by_user[user_id_str] = []
        self._categories_by_user[user_id_str].append(category_id)
        
        return category
    
    async def get_by_id(
        self, category_id: UUID, user_id: Optional[UUID] = None
    ) -> Optional[Category]:
        """Busca categoria por ID (sistema ou usuário)."""
        category = self._categories.get(str(category_id))
        if not category or not category.is_active:
            return None
        
        # Categoria do sistema é acessível a todos
        if category.is_system:
            return category
        
        # Categoria do usuário deve pertencer ao usuário
        if user_id and category.user_id == user_id:
            return category
        
        return None
    
    async def get_by_user_id(
        self,
        user_id: UUID,
        category_type: Optional[TransactionType] = None,
        include_system: bool = True
    ) -> List[Category]:
        """Lista categorias do usuário + sistema."""
        categories = []
        
        # Categorias do usuário
        user_id_str = str(user_id)
        user_category_ids = self._categories_by_user.get(user_id_str, [])
        for cat_id in user_category_ids:
            category = self._categories.get(cat_id)
            if category and category.is_active:
                if not category_type or category.type == category_type:
                    categories.append(category)
        
        # Categorias do sistema se solicitadas
        if include_system:
            system_category_ids = self._categories_by_user.get("system", [])
            for cat_id in system_category_ids:
                category = self._categories.get(cat_id)
                if category and category.is_active:
                    if not category_type or category.type == category_type:
                        categories.append(category)
        
        return categories
    
    async def get_by_name_and_user(
        self, name: str, user_id: UUID, category_type: TransactionType
    ) -> Optional[Category]:
        """Busca categoria por nome, usuário e tipo."""
        user_categories = await self.get_by_user_id(
            user_id, category_type, include_system=False
        )
        
        for category in user_categories:
            if category.name.lower() == name.lower():
                return category
        
        return None
    
    async def update(self, category: Category) -> Category:
        """Atualiza uma categoria existente."""
        category_id = str(category.id)
        category.updated_at = datetime.utcnow()
        self._categories[category_id] = category
        return category
    
    async def delete(self, category_id: UUID, user_id: UUID) -> bool:
        """Remove categoria (soft delete)."""
        category = await self.get_by_id(category_id, user_id)
        if not category:
            raise CategoryNotFoundError(str(category_id), str(user_id))
        
        if category.is_system:
            raise CannotDeleteSystemCategoryError(str(category_id))
        
        if category.user_id != user_id:
            raise CategoryNotFoundError(str(category_id), str(user_id))
        
        # Verificar se está em uso (simulado)
        # Em implementação real, verificaria transações
        usage_count = 0  # Placeholder
        if usage_count > 0:
            raise CategoryInUseError(str(category_id), usage_count)
        
        category.deactivate()
        await self.update(category)
        return True
    
    async def get_system_categories(
        self, category_type: Optional[TransactionType] = None
    ) -> List[Category]:
        """Lista categorias do sistema."""
        categories = []
        system_category_ids = self._categories_by_user.get("system", [])
        
        for cat_id in system_category_ids:
            category = self._categories.get(cat_id)
            if category and category.is_active and category.is_system:
                if not category_type or category.type == category_type:
                    categories.append(category)
        
        return categories
    
    async def initialize_system_categories(self) -> None:
        """Inicializa categorias padrão do sistema."""
        if self._system_categories_initialized:
            return
        
        # Categorias de receita
        income_categories = [
            "Salário",
            "Freelance",
            "Investimentos",
            "Aluguéis",
            "Vendas",
            "Bonificação",
            "Outros"
        ]
        
        for name in income_categories:
            category = Category.create_system_category(
                name, TransactionType.INCOME
            )
            await self.create(category)
        
        # Categorias de despesa
        expense_categories = [
            "Alimentação",
            "Transporte",
            "Moradia",
            "Saúde",
            "Educação",
            "Lazer",
            "Roupas",
            "Tecnologia",
            "Serviços",
            "Impostos",
            "Outros"
        ]
        
        for name in expense_categories:
            category = Category.create_system_category(
                name, TransactionType.EXPENSE
            )
            await self.create(category)
        
        self._system_categories_initialized = True
    
    def clear(self) -> None:
        """Limpa todos os dados do repositório."""
        self._categories.clear()
        self._categories_by_user.clear()
        self._system_categories_initialized = False


class InMemoryGoalRepository(GoalRepository):
    """Implementação in-memory do repositório de metas."""

    def __init__(self) -> None:
        self._goals: Dict[str, Goal] = {}
        self._goals_by_user: Dict[str, List[str]] = {}

    async def create(self, goal: Goal) -> Goal:
        """Cria uma nova meta no repositório."""
        if goal.id is None:
            goal.id = str(uuid.uuid4())
        
        goal_id = str(goal.id)
        user_id = str(goal.user_id)

        self._goals[goal_id] = goal

        if user_id not in self._goals_by_user:
            self._goals_by_user[user_id] = []
        self._goals_by_user[user_id].append(goal_id)

        return goal

    async def get_by_id(self, goal_id: str, user_id: UUID) -> Optional[Goal]:
        """Busca meta por ID validando propriedade."""
        goal = self._goals.get(goal_id)
        if goal and UUID(goal.user_id) == user_id:
            return goal
        return None

    async def get_by_user_id(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> List[Goal]:
        """Lista metas do usuário."""
        user_id_str = str(user_id)
        goal_ids = self._goals_by_user.get(user_id_str, [])

        all_goals = [
            self._goals[gid] for gid in goal_ids if gid in self._goals
        ]
        
        # Ordenar por data de criação (mais recentes primeiro)
        all_goals.sort(key=lambda g: g.created_at, reverse=True)

        return all_goals[offset:offset + limit]

    async def update(self, goal: Goal) -> Goal:
        """Atualiza uma meta existente."""
        goal_id = str(goal.id)
        if goal_id not in self._goals:
            raise GoalNotFoundError(goal_id)

        goal.updated_at = datetime.utcnow()
        self._goals[goal_id] = goal
        return goal

    async def delete(self, goal_id: str, user_id: UUID) -> bool:
        """Remove uma meta (hard delete)."""
        goal = await self.get_by_id(goal_id, user_id)
        if not goal:
            return False

        # Hard delete
        del self._goals[goal_id]
        
        user_goals = self._goals_by_user.get(str(user_id), [])
        if goal_id in user_goals:
            user_goals.remove(goal_id)

        return True

    def clear(self) -> None:
        """Limpa todos os dados do repositório."""
        self._goals.clear()
        self._goals_by_user.clear()


class InMemoryBudgetRepository(BudgetRepository):
    """Implementação in-memory do repositório de orçamentos."""

    def __init__(self) -> None:
        self._budgets: Dict[str, Budget] = {}
        self._budgets_by_user_month: Dict[str, List[str]] = {}

    async def upsert(self, budget: Budget) -> Budget:
        """Cria ou atualiza um orçamento."""
        if budget.id is None:
            budget.id = str(uuid.uuid4())

        budget_id = str(budget.id)
        user_id = str(budget.user_id)
        month_key = budget.month.strftime("%Y-%m")
        user_month_key = f"{user_id}_{month_key}"

        # Check for existing budget for the same user, category, and month
        existing_budgets = self._budgets_by_user_month.get(user_month_key, [])
        for b_id in existing_budgets:
            existing_budget = self._budgets.get(b_id)
            if (
                existing_budget
                and existing_budget.category_id == budget.category_id
            ):
                # Update existing budget
                existing_budget.amount = budget.amount
                existing_budget.updated_at = datetime.utcnow()
                return existing_budget

        # Create new budget
        self._budgets[budget_id] = budget
        if user_month_key not in self._budgets_by_user_month:
            self._budgets_by_user_month[user_month_key] = []
        self._budgets_by_user_month[user_month_key].append(budget_id)
        return budget

    async def get_by_id(
        self, budget_id: str, user_id: UUID
    ) -> Optional[Budget]:
        """Busca orçamento por ID."""
        budget = self._budgets.get(budget_id)
        if budget and budget.user_id == user_id:
            return budget
        return None

    async def get_by_user_and_month(
        self, user_id: UUID, month: datetime
    ) -> List[Budget]:
        """Lista orçamentos de um usuário para um mês específico."""
        user_id_str = str(user_id)
        month_key = month.strftime("%Y-%m")
        user_month_key = f"{user_id_str}_{month_key}"

        budget_ids = self._budgets_by_user_month.get(user_month_key, [])
        return [
            self._budgets[b_id] for b_id in budget_ids if b_id in self._budgets
        ]

    async def delete(self, budget_id: str, user_id: UUID) -> bool:
        """Exclui um orçamento."""
        budget = await self.get_by_id(budget_id, user_id)
        if not budget:
            return False

        del self._budgets[budget_id]

        user_id_str = str(budget.user_id)
        month_key = budget.month.strftime("%Y-%m")
        user_month_key = f"{user_id_str}_{month_key}"
        
        user_budgets = self._budgets_by_user_month.get(user_month_key, [])
        if budget_id in user_budgets:
            user_budgets.remove(budget_id)
        
        return True

    def clear(self) -> None:
        """Limpa todos os dados do repositório."""
        self._budgets.clear()
        self._budgets_by_user_month.clear()
