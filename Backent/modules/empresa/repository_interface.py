"""
Interface del repositorio de Empresa.
Define el contrato para operaciones de base de datos del módulo de empresa.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from .model import Empresa
from .schemas import EmpresaCreate, EmpresaUpdate


class EmpresaRepositoryInterface(ABC):
    """Interface para el repositorio de empresa."""

    @abstractmethod
    def get_empresa(self, empresa_id: int) -> Optional[Empresa]:
        """Obtiene una empresa por su ID."""
        pass

    @abstractmethod
    def get_empresa_by_ruc(self, ruc: str) -> Optional[Empresa]:
        """Obtiene una empresa por su RUC."""
        pass

    @abstractmethod
    def get_empresas(self, skip: int = 0, limit: int = 100) -> List[Empresa]:
        """Obtiene lista de empresas con paginación."""
        pass

    @abstractmethod
    def create_empresa(self, empresa: EmpresaCreate) -> Empresa:
        """Crea una nueva empresa."""
        pass

    @abstractmethod
    def update_empresa(self, empresa_id: int, empresa: EmpresaUpdate) -> Optional[Empresa]:
        """Actualiza una empresa existente."""
        pass

    @abstractmethod
    def delete_empresa(self, empresa_id: int) -> Optional[Empresa]:
        """Elimina (soft delete) una empresa."""
        pass
