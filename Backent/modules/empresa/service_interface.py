"""
Interface del servicio de Empresa.
Define el contrato para la lógica de negocio del módulo de empresa.
"""

from abc import ABC, abstractmethod
from typing import List

from .model import Empresa
from .schemas import EmpresaCreate, EmpresaUpdate


class EmpresaServiceInterface(ABC):
    """Interface para el servicio de empresa."""

    @abstractmethod
    def create_empresa(self, empresa: EmpresaCreate) -> Empresa:
        """Crea una nueva empresa."""
        pass

    @abstractmethod
    def get_empresas(self, skip: int = 0, limit: int = 100) -> List[Empresa]:
        """Obtiene lista de empresas con paginación."""
        pass

    @abstractmethod
    def get_empresa(self, empresa_id: int) -> Empresa:
        """Obtiene una empresa por su ID."""
        pass

    @abstractmethod
    def update_empresa(self, empresa_id: int, empresa: EmpresaUpdate) -> Empresa:
        """Actualiza una empresa existente."""
        pass

    @abstractmethod
    def delete_empresa(self, empresa_id: int) -> Empresa:
        """Elimina (soft delete) una empresa."""
        pass
