"""
Interface del repositorio de Proveedores.
Define el contrato para operaciones de base de datos del módulo de proveedores.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from .model import Proveedor
from .schemas import ProveedorCreate, ProveedorUpdate


class ProveedorRepositoryInterface(ABC):
    """Interface para el repositorio de proveedores."""

    @abstractmethod
    def get_proveedor(self, proveedor_id: int) -> Optional[Proveedor]:
        """Obtiene un proveedor por su ID."""
        pass

    @abstractmethod
    def get_proveedor_by_ruc_dni(self, ruc_dni: str) -> Optional[Proveedor]:
        """Obtiene un proveedor por su RUC/DNI."""
        pass

    @abstractmethod
    def get_proveedores(self, skip: int = 0, limit: int = 100) -> List[Proveedor]:
        """Obtiene lista de proveedores con paginación."""
        pass

    @abstractmethod
    def create_proveedor(self, proveedor: ProveedorCreate) -> Proveedor:
        """Crea un nuevo proveedor."""
        pass

    @abstractmethod
    def update_proveedor(self, proveedor_id: int, proveedor: ProveedorUpdate) -> Optional[Proveedor]:
        """Actualiza un proveedor existente."""
        pass

    @abstractmethod
    def delete_proveedor(self, proveedor_id: int) -> Optional[Proveedor]:
        """Elimina (soft delete) un proveedor."""
        pass
