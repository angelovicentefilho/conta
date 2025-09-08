"""
Controller REST para gestão de transações financeiras.

Implementa todos os endpoints de CRUD para transações, com validações
de entrada, autorização e tratamento de erros.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.adapters.inbound.auth_middleware import get_current_user
from app.core.domain.user import User
from app.core.domain.transaction import (
    CreateTransactionRequest,
    UpdateTransactionRequest,
    TransactionResponse,
    TransactionSummaryResponse,
    TransactionType,
)
from app.core.services.transaction_service import TransactionServiceImpl
from app.core.domain.exceptions import (
    TransactionNotFoundError,
    InvalidTransactionAmountError,
    CategoryNotFoundError,
    AccountNotFoundError,
)

# Dependências de serviços (instância global para desenvolvimento)
from app.adapters.outbound.memory_repositories import (
    InMemoryTransactionRepository,
    InMemoryCategoryRepository,
)
from app.adapters.inbound.account_controller import _account_repository

_transaction_repository = InMemoryTransactionRepository()
_category_repository = InMemoryCategoryRepository()
_transaction_service = TransactionServiceImpl(
    _transaction_repository,
    _category_repository,
    _account_repository
)


def get_transaction_service() -> TransactionServiceImpl:
    """Factory para criar instância do serviço de transações."""
    return _transaction_service


# Router para endpoints de transações
router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_transaction(
    transaction_data: CreateTransactionRequest,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionServiceImpl = Depends(
        get_transaction_service
    )
) -> TransactionResponse:
    """
    Cria uma nova transação financeira.
    
    Args:
        transaction_data: Dados da transação a ser criada
        current_user: Usuário autenticado
        transaction_service: Serviço de transações
    
    Returns:
        TransactionResponse: Dados da transação criada
    
    Raises:
        HTTPException: Se houver erro na validação ou criação
    """
    try:
        transaction = await transaction_service.create_transaction(
            user_id=UUID(current_user.id),
            account_id=transaction_data.account_id,
            category_id=transaction_data.category_id,
            transaction_type=transaction_data.type,
            amount=float(transaction_data.amount),
            description=transaction_data.description,
            date=transaction_data.date,
            is_recurring=transaction_data.is_recurring,
            recurrence_frequency=(
                transaction_data.recurrence_frequency.value
                if transaction_data.recurrence_frequency else None
            )
        )
        
        # Buscar nomes de conta e categoria para resposta
        account = await _account_repository.get_by_id(
            transaction.account_id, UUID(current_user.id)
        )
        category = await _category_repository.get_by_id(
            transaction.category_id, UUID(current_user.id)
        )
        
        return TransactionResponse(
            id=transaction.id,
            account_id=transaction.account_id,
            account_name=account.name if account else "Conta não encontrada",
            category_id=transaction.category_id,
            category_name=category.name if category else "Categoria não encontrada",
            type=transaction.type,
            amount=transaction.amount,
            description=transaction.description,
            date=transaction.date,
            is_recurring=transaction.is_recurring,
            recurrence_frequency=transaction.recurrence_frequency,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at
        )
        
    except (AccountNotFoundError, CategoryNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InvalidTransactionAmountError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[TransactionSummaryResponse])
async def list_transactions(
    account_id: Optional[UUID] = Query(None, description="Filtrar por conta"),
    category_id: Optional[UUID] = Query(None, description="Filtrar por categoria"),
    transaction_type: Optional[TransactionType] = Query(
        None, description="Filtrar por tipo"
    ),
    start_date: Optional[datetime] = Query(
        None, description="Data inicial (ISO format)"
    ),
    end_date: Optional[datetime] = Query(
        None, description="Data final (ISO format)"
    ),
    limit: int = Query(50, ge=1, le=100, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionServiceImpl = Depends(get_transaction_service)
) -> List[TransactionSummaryResponse]:
    """
    Lista transações do usuário com filtros opcionais.
    
    Args:
        account_id: ID da conta para filtrar (opcional)
        category_id: ID da categoria para filtrar (opcional)
        transaction_type: Tipo de transação para filtrar (opcional)
        start_date: Data inicial para filtrar (opcional)
        end_date: Data final para filtrar (opcional)
        limit: Número máximo de resultados
        offset: Offset para paginação
        current_user: Usuário autenticado
        transaction_service: Serviço de transações
    
    Returns:
        List[TransactionSummaryResponse]: Lista de transações
    """
    try:
        transactions = await transaction_service.list_transactions(
            user_id=UUID(current_user.id),
            account_id=account_id,
            category_id=category_id,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        # Converter para response com nomes
        result = []
        for transaction in transactions:
            # Buscar nomes de conta e categoria
            account = await _account_repository.get_by_id(
                transaction.account_id, UUID(current_user.id)
            )
            category = await _category_repository.get_by_id(
                transaction.category_id, UUID(current_user.id)
            )
            
            result.append(TransactionSummaryResponse(
                id=transaction.id,
                account_name=account.name if account else "Conta não encontrada",
                category_name=category.name if category else "Categoria não encontrada",
                type=transaction.type,
                amount=transaction.amount,
                description=transaction.description,
                date=transaction.date
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar transações: {str(e)}"
        )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionServiceImpl = Depends(get_transaction_service)
) -> TransactionResponse:
    """
    Busca uma transação específica por ID.
    
    Args:
        transaction_id: ID da transação
        current_user: Usuário autenticado
        transaction_service: Serviço de transações
    
    Returns:
        TransactionResponse: Dados da transação
    
    Raises:
        HTTPException: Se transação não for encontrada
    """
    try:
        transaction = await transaction_service.get_transaction_by_id(
            transaction_id, UUID(current_user.id)
        )
        
        # Buscar nomes de conta e categoria
        account = await _account_repository.get_by_id(
            transaction.account_id, UUID(current_user.id)
        )
        category = await _category_repository.get_by_id(
            transaction.category_id, UUID(current_user.id)
        )
        
        return TransactionResponse(
            id=transaction.id,
            account_id=transaction.account_id,
            account_name=account.name if account else "Conta não encontrada",
            category_id=transaction.category_id,
            category_name=category.name if category else "Categoria não encontrada",
            type=transaction.type,
            amount=transaction.amount,
            description=transaction.description,
            date=transaction.date,
            is_recurring=transaction.is_recurring,
            recurrence_frequency=transaction.recurrence_frequency,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at
        )
        
    except TransactionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: UUID,
    transaction_data: UpdateTransactionRequest,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionServiceImpl = Depends(get_transaction_service)
) -> TransactionResponse:
    """
    Atualiza uma transação existente.
    
    Args:
        transaction_id: ID da transação
        transaction_data: Novos dados da transação
        current_user: Usuário autenticado
        transaction_service: Serviço de transações
    
    Returns:
        TransactionResponse: Dados da transação atualizada
    
    Raises:
        HTTPException: Se houver erro na validação ou atualização
    """
    try:
        transaction = await transaction_service.update_transaction(
            transaction_id=transaction_id,
            user_id=UUID(current_user.id),
            account_id=transaction_data.account_id,
            category_id=transaction_data.category_id,
            transaction_type=transaction_data.type,
            amount=float(transaction_data.amount) if transaction_data.amount else None,
            description=transaction_data.description,
            date=transaction_data.date,
            is_recurring=transaction_data.is_recurring,
            recurrence_frequency=(
                transaction_data.recurrence_frequency.value
                if transaction_data.recurrence_frequency else None
            )
        )
        
        # Buscar nomes de conta e categoria
        account = await _account_repository.get_by_id(
            transaction.account_id, UUID(current_user.id)
        )
        category = await _category_repository.get_by_id(
            transaction.category_id, UUID(current_user.id)
        )
        
        return TransactionResponse(
            id=transaction.id,
            account_id=transaction.account_id,
            account_name=account.name if account else "Conta não encontrada",
            category_id=transaction.category_id,
            category_name=category.name if category else "Categoria não encontrada",
            type=transaction.type,
            amount=transaction.amount,
            description=transaction.description,
            date=transaction.date,
            is_recurring=transaction.is_recurring,
            recurrence_frequency=transaction.recurrence_frequency,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at
        )
        
    except TransactionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except (AccountNotFoundError, CategoryNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except (InvalidTransactionAmountError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionServiceImpl = Depends(get_transaction_service)
) -> None:
    """
    Remove uma transação.
    
    Args:
        transaction_id: ID da transação
        current_user: Usuário autenticado
        transaction_service: Serviço de transações
    
    Raises:
        HTTPException: Se transação não for encontrada
    """
    try:
        await transaction_service.delete_transaction(
            transaction_id, UUID(current_user.id)
        )
    except TransactionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{transaction_id}/duplicate", response_model=TransactionResponse)
async def duplicate_transaction(
    transaction_id: UUID,
    new_date: datetime,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionServiceImpl = Depends(get_transaction_service)
) -> TransactionResponse:
    """
    Duplica uma transação com nova data.
    
    Args:
        transaction_id: ID da transação a ser duplicada
        new_date: Nova data para a transação duplicada
        current_user: Usuário autenticado
        transaction_service: Serviço de transações
    
    Returns:
        TransactionResponse: Dados da nova transação
    
    Raises:
        HTTPException: Se transação não for encontrada
    """
    try:
        transaction = await transaction_service.duplicate_transaction(
            transaction_id, UUID(current_user.id), new_date
        )
        
        # Buscar nomes de conta e categoria
        account = await _account_repository.get_by_id(
            transaction.account_id, UUID(current_user.id)
        )
        category = await _category_repository.get_by_id(
            transaction.category_id, UUID(current_user.id)
        )
        
        return TransactionResponse(
            id=transaction.id,
            account_id=transaction.account_id,
            account_name=account.name if account else "Conta não encontrada",
            category_id=transaction.category_id,
            category_name=category.name if category else "Categoria não encontrada",
            type=transaction.type,
            amount=transaction.amount,
            description=transaction.description,
            date=transaction.date,
            is_recurring=transaction.is_recurring,
            recurrence_frequency=transaction.recurrence_frequency,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at
        )
        
    except TransactionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
