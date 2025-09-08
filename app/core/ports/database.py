"""
Porta para operações de banco de dados.

Define a interface para persistência de dados seguindo o padrão Repository.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic

T = TypeVar('T')


class DatabasePort(ABC, Generic[T]):
    """
    Interface base para operações de banco de dados.
    
    Esta porta define os métodos essenciais que qualquer adaptador
    de banco de dados deve implementar para ser compatível com a aplicação.
    """
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """
        Cria uma nova entidade no banco de dados.
        
        Args:
            entity: Entidade a ser criada
            
        Returns:
            Entidade criada com ID gerado
            
        Raises:
            DatabaseError: Erro ao criar entidade
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """
        Busca uma entidade pelo ID.
        
        Args:
            entity_id: ID da entidade
            
        Returns:
            Entidade encontrada ou None se não existir
        """
        pass
    
    @abstractmethod
    async def update(self, entity_id: str, update_data: Dict[str, Any]) -> Optional[T]:
        """
        Atualiza uma entidade existente.
        
        Args:
            entity_id: ID da entidade a ser atualizada
            update_data: Dados para atualização
            
        Returns:
            Entidade atualizada ou None se não encontrada
        """
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """
        Remove uma entidade do banco de dados.
        
        Args:
            entity_id: ID da entidade a ser removida
            
        Returns:
            True se removida com sucesso, False se não encontrada
        """
        pass
    
    @abstractmethod
    async def list_all(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[T]:
        """
        Lista entidades com filtros opcionais.
        
        Args:
            filters: Filtros a serem aplicados
            limit: Limite de resultados
            offset: Offset para paginação
            
        Returns:
            Lista de entidades encontradas
        """
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Conta o número de entidades que atendem aos filtros.
        
        Args:
            filters: Filtros a serem aplicados
            
        Returns:
            Número de entidades encontradas
        """
        pass
