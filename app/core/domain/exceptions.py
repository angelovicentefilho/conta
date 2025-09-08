from typing import Optional


class FinAppException(Exception):
    """Base exception for the application."""
    pass


class AccountAlreadyExistsError(FinAppException):
    def __init__(self, name: str, user_id: str):
        super().__init__(
            f"Account '{name}' already exists for user '{user_id}'."
        )


class AccountNameNotUniqueError(FinAppException):
    def __init__(self, name: str):
        super().__init__(f"Account name '{name}' is not unique.")


class CannotDeleteLastAccountError(FinAppException):
    def __init__(self) -> None:
        super().__init__("Cannot delete the last account.")


class InvalidAccountTypeError(FinAppException):
    def __init__(self, account_type: str):
        super().__init__(f"Invalid account type: {account_type}.")


class InvalidBalanceError(FinAppException):
    def __init__(self, balance: float):
        super().__init__(f"Invalid balance: {balance}.")


class InvalidTransactionAmountError(FinAppException):
    def __init__(self, amount: float):
        super().__init__(f"Invalid transaction amount: {amount}.")


class TransactionError(FinAppException):
    """Base exception for transaction errors."""
    pass


class AccountNotFoundError(FinAppException):
    def __init__(self, account_id: str, user_id: Optional[str] = None):
        if user_id:
            super().__init__(
                f"Account '{account_id}' not found for user '{user_id}'."
            )
        else:
            super().__init__(f"Account '{account_id}' not found.")


class TransactionNotFoundError(FinAppException):
    def __init__(self, transaction_id: str, user_id: Optional[str] = None):
        if user_id:
            super().__init__(
                f"Transaction '{transaction_id}' "
                f"not found for user '{user_id}'."
            )
        else:
            super().__init__(f"Transaction '{transaction_id}' not found.")


class CategoryAlreadyExistsError(FinAppException):
    def __init__(self, name: str, user_id: str):
        super().__init__(
            f"Category '{name}' already exists for user '{user_id}'."
        )


class CategoryNameNotUniqueError(FinAppException):
    def __init__(self, name: str):
        super().__init__(f"Category name '{name}' is not unique.")


class CategoryNotFoundError(FinAppException):
    def __init__(self, category_id: str, user_id: Optional[str] = None):
        if user_id:
            super().__init__(
                f"Category '{category_id}' not found for user '{user_id}'."
            )
        else:
            super().__init__(f"Category '{category_id}' not found.")


class CannotDeleteSystemCategoryError(FinAppException):
    def __init__(self, category_id: str):
        super().__init__(f"System category '{category_id}' cannot be deleted.")


class CategoryInUseError(FinAppException):
    def __init__(self, category_id: str, count: int):
        super().__init__(
            f"Category '{category_id}' is in use by {count} transactions."
        )


class GoalNotFoundError(FinAppException):
    def __init__(self, goal_id: str, user_id: Optional[str] = None):
        if user_id:
            super().__init__(
                f"Goal '{goal_id}' not found for user '{user_id}'."
            )
        else:
            super().__init__(f"Goal '{goal_id}' not found.")


class InvalidGoalAmountError(FinAppException):
    def __init__(self, amount: float):
        super().__init__(f"Invalid goal amount: {amount}. Must be positive.")


class GoalAlreadyCompletedError(FinAppException):
    def __init__(self, goal_id: str):
        super().__init__(f"Goal '{goal_id}' is already completed.")


class GoalDeadlinePassedError(FinAppException):
    def __init__(self, message: str):
        super().__init__(message)


class BudgetNotFoundError(FinAppException):
    def __init__(self, budget_id: str, user_id: Optional[str] = None):
        if user_id:
            super().__init__(
                f"Budget '{budget_id}' not found for user '{user_id}'."
            )
        else:
            super().__init__(f"Budget '{budget_id}' not found.")
