"""
Controller REST para gestão de contas financeiras.

Implementa todos os endpoints de CRUD para contas, com validações
de entrada, autorização e tratamento de erros.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.adapters.inbound.auth_middleware import get_current_user
from app.core.domain.user import User
from app.core.domain.account import (
    CreateAccountRequest,
    UpdateAccountRequest,
    AccountResponse,
    AccountSummaryResponse,
)
from app.core.services.account_service import AccountServiceImpl
from app.core.domain.exceptions import (
    AccountNotFoundError,
    AccountNameNotUniqueError,
    InvalidAccountTypeError,
    InvalidBalanceError,
    CannotDeleteLastAccountError,
)

# Dependências de serviços (instância global para desenvolvimento)
from app.adapters.outbound.memory_repositories import (
    InMemoryAccountRepository
)

_account_repository = InMemoryAccountRepository()
_account_service = AccountServiceImpl(_account_repository)


def get_account_service() -> AccountServiceImpl:
    """Factory para criar instância do serviço de contas."""
    return _account_service


# Router para endpoints de contas
router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])


@router.post(
    "/",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_account(
    account_data: CreateAccountRequest,
    current_user: User = Depends(get_current_user),
    account_service: AccountServiceImpl = Depends(get_account_service)
) -> AccountResponse:
    """
    Cria uma nova conta financeira.
    
    Args:
        account_data: Dados da conta a ser criada
        current_user: Usuário autenticado
        account_service: Serviço de contas
        
    Returns:
        AccountResponse: Dados da conta criada
        
    Raises:
        HTTPException: Em caso de erro de validação ou negócio
    """
    try:
        account = await account_service.create_account(
            user_id=UUID(current_user.id),
            name=account_data.name,
            account_type=account_data.type.value,
            balance=float(account_data.balance),
            is_primary=account_data.is_primary
        )
        
        return AccountResponse(
            id=account.id,
            name=account.name,
            type=account.type,
            balance=account.balance,
            is_primary=account.is_primary,
            created_at=account.created_at,
            updated_at=account.updated_at,
            is_active=account.is_active
        )
        
    except AccountNameNotUniqueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidAccountTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidBalanceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[AccountSummaryResponse])
async def list_accounts(
    current_user: User = Depends(get_current_user),
    account_service: AccountServiceImpl = Depends(get_account_service)
) -> List[AccountSummaryResponse]:
    """
    Lista todas as contas do usuário autenticado.
    
    Args:
        current_user: Usuário autenticado
        account_service: Serviço de contas
        
    Returns:
        Lista de contas resumidas ordenadas (principal primeiro)
    """
    accounts = await account_service.get_user_accounts(UUID(current_user.id))
    
    return [
        AccountSummaryResponse(
            id=account.id,
            name=account.name,
            type=account.type,
            balance=account.balance,
            is_primary=account.is_primary
        )
        for account in accounts
    ]


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    account_service: AccountServiceImpl = Depends(get_account_service)
) -> AccountResponse:
    """
    Obtém detalhes de uma conta específica.
    
    Args:
        account_id: ID da conta
        current_user: Usuário autenticado
        account_service: Serviço de contas
        
    Returns:
        AccountResponse: Detalhes completos da conta
        
    Raises:
        HTTPException: Se conta não encontrada ou não pertencer ao usuário
    """
    try:
        account = await account_service.get_account(
            account_id, UUID(current_user.id)
        )
        
        return AccountResponse(
            id=account.id,
            name=account.name,
            type=account.type,
            balance=account.balance,
            is_primary=account.is_primary,
            created_at=account.created_at,
            updated_at=account.updated_at,
            is_active=account.is_active
        )
        
    except AccountNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada"
        )


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: UUID,
    account_data: UpdateAccountRequest,
    current_user: User = Depends(get_current_user),
    account_service: AccountServiceImpl = Depends(get_account_service)
) -> AccountResponse:
    """
    Atualiza dados de uma conta existente.
    
    Args:
        account_id: ID da conta
        account_data: Dados para atualização
        current_user: Usuário autenticado
        account_service: Serviço de contas
        
    Returns:
        AccountResponse: Conta atualizada
        
    Raises:
        HTTPException: Em caso de erro de validação ou negócio
    """
    try:
        account = await account_service.update_account(
            account_id=account_id,
            user_id=UUID(current_user.id),
            name=account_data.name,
            account_type=(
                account_data.type.value if account_data.type else None
            ),
            balance=(
                float(account_data.balance) if account_data.balance else None
            )
        )
        
        return AccountResponse(
            id=account.id,
            name=account.name,
            type=account.type,
            balance=account.balance,
            is_primary=account.is_primary,
            created_at=account.created_at,
            updated_at=account.updated_at,
            is_active=account.is_active
        )
        
    except AccountNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada"
        )
    except AccountNameNotUniqueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidAccountTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidBalanceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    account_service: AccountServiceImpl = Depends(get_account_service)
) -> None:
    """
    Remove uma conta financeira.
    
    Args:
        account_id: ID da conta
        current_user: Usuário autenticado
        account_service: Serviço de contas
        
    Raises:
        HTTPException: Em caso de erro de validação ou negócio
    """
    try:
        await account_service.delete_account(account_id, UUID(current_user.id))
        
    except AccountNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada"
        )
    except CannotDeleteLastAccountError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{account_id}/set-primary", response_model=AccountResponse)
async def set_primary_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    account_service: AccountServiceImpl = Depends(get_account_service)
) -> AccountResponse:
    """
    Define uma conta como principal.
    
    Args:
        account_id: ID da conta
        current_user: Usuário autenticado
        account_service: Serviço de contas
        
    Returns:
        AccountResponse: Conta atualizada como principal
        
    Raises:
        HTTPException: Se conta não encontrada
    """
    try:
        account = await account_service.set_primary_account(
            account_id, UUID(current_user.id)
        )
        
        return AccountResponse(
            id=account.id,
            name=account.name,
            type=account.type,
            balance=account.balance,
            is_primary=account.is_primary,
            created_at=account.created_at,
            updated_at=account.updated_at,
            is_active=account.is_active
        )
        
    except AccountNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada"
        )
