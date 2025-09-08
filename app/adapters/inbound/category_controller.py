"""
Controller REST para gestão de categorias de transações.

Implementa endpoints para listar e criar categorias personalizadas.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.adapters.inbound.auth_middleware import get_current_user
from app.core.domain.user import User
from app.core.domain.transaction import (
    CreateCategoryRequest,
    CategoryResponse,
    TransactionType,
)
from app.core.services.transaction_service import CategoryServiceImpl
from app.core.domain.exceptions import (
    CategoryNotFoundError,
    CategoryAlreadyExistsError,
    CategoryNameNotUniqueError,
    CannotDeleteSystemCategoryError,
)

# Dependências de serviços (usar mesma instância do transaction_controller)
from app.adapters.inbound.transaction_controller import _category_repository

_category_service = CategoryServiceImpl(_category_repository)


def get_category_service() -> CategoryServiceImpl:
    """Factory para criar instância do serviço de categorias."""
    return _category_service


# Router para endpoints de categorias
router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    transaction_type: Optional[TransactionType] = None,
    current_user: User = Depends(get_current_user),
    category_service: CategoryServiceImpl = Depends(get_category_service)
) -> List[CategoryResponse]:
    """
    Lista todas as categorias disponíveis para o usuário.
    
    Inclui categorias do sistema e categorias personalizadas do usuário.
    
    Args:
        transaction_type: Filtrar por tipo de transação (opcional)
        current_user: Usuário autenticado
        category_service: Serviço de categorias
    
    Returns:
        List[CategoryResponse]: Lista de categorias
    """
    try:
        # Inicializar categorias do sistema se necessário
        await category_service.initialize_default_categories()
        
        categories = await category_service.list_categories(
            UUID(current_user.id), transaction_type
        )
        
        return [
            CategoryResponse(
                id=category.id,
                name=category.name,
                type=category.type,
                is_system=category.is_system,
                created_at=category.created_at
            )
            for category in categories
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar categorias: {str(e)}"
        )


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_category(
    category_data: CreateCategoryRequest,
    current_user: User = Depends(get_current_user),
    category_service: CategoryServiceImpl = Depends(get_category_service)
) -> CategoryResponse:
    """
    Cria uma nova categoria personalizada para o usuário.
    
    Args:
        category_data: Dados da categoria a ser criada
        current_user: Usuário autenticado
        category_service: Serviço de categorias
    
    Returns:
        CategoryResponse: Dados da categoria criada
    
    Raises:
        HTTPException: Se houver erro na validação ou criação
    """
    try:
        category = await category_service.create_category(
            user_id=UUID(current_user.id),
            name=category_data.name,
            category_type=category_data.type
        )
        
        return CategoryResponse(
            id=category.id,
            name=category.name,
            type=category.type,
            is_system=category.is_system,
            created_at=category.created_at
        )
        
    except CategoryAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    current_user: User = Depends(get_current_user),
    category_service: CategoryServiceImpl = Depends(get_category_service)
) -> CategoryResponse:
    """
    Busca uma categoria específica por ID.
    
    Args:
        category_id: ID da categoria
        current_user: Usuário autenticado
        category_service: Serviço de categorias
    
    Returns:
        CategoryResponse: Dados da categoria
    
    Raises:
        HTTPException: Se categoria não for encontrada
    """
    try:
        category = await category_service.get_category_by_id(
            category_id, UUID(current_user.id)
        )
        
        return CategoryResponse(
            id=category.id,
            name=category.name,
            type=category.type,
            is_system=category.is_system,
            created_at=category.created_at
        )
        
    except CategoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category_data: CreateCategoryRequest,
    current_user: User = Depends(get_current_user),
    category_service: CategoryServiceImpl = Depends(get_category_service)
) -> CategoryResponse:
    """
    Atualiza o nome de uma categoria personalizada.
    
    Args:
        category_id: ID da categoria
        category_data: Novos dados da categoria
        current_user: Usuário autenticado
        category_service: Serviço de categorias
    
    Returns:
        CategoryResponse: Dados da categoria atualizada
    
    Raises:
        HTTPException: Se houver erro na validação ou atualização
    """
    try:
        category = await category_service.update_category(
            category_id, UUID(current_user.id), category_data.name
        )
        
        return CategoryResponse(
            id=category.id,
            name=category.name,
            type=category.type,
            is_system=category.is_system,
            created_at=category.created_at
        )
        
    except CategoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except (CannotDeleteSystemCategoryError, CategoryNameNotUniqueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    current_user: User = Depends(get_current_user),
    category_service: CategoryServiceImpl = Depends(get_category_service)
) -> None:
    """
    Remove uma categoria personalizada.
    
    Args:
        category_id: ID da categoria
        current_user: Usuário autenticado
        category_service: Serviço de categorias
    
    Raises:
        HTTPException: Se categoria não for encontrada ou não puder ser deletada
    """
    try:
        await category_service.delete_category(
            category_id, UUID(current_user.id)
        )
    except CategoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except CannotDeleteSystemCategoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
