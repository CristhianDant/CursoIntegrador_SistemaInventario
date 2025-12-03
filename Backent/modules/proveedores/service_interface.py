"""
Interface del servicio de Proveedores.
Define el contrato para la lógica de negocio del módulo de proveedores.
"""

from abc import ABC, abstractmethod
from typing import List

from .model import Proveedor
from .schemas import ProveedorCreate, ProveedorUpdate


class ProveedorServiceInterface(ABC):
    """Interface para el servicio de proveedores."""

    @abstractmethod
    def create_proveedor(self, proveedor: ProveedorCreate) -> Proveedor:
        """Crea un nuevo proveedor."""
        pass

    @abstractmethod
    def get_proveedores(self, skip: int = 0, limit: int = 100) -> List[Proveedor]:
        """Obtiene lista de proveedores con paginación."""
        pass

    @abstractmethod
    def get_proveedor(self, proveedor_id: int) -> Proveedor:
        """Obtiene un proveedor por su ID."""
        pass

    @abstractmethod
    def update_proveedor(self, proveedor_id: int, proveedor: ProveedorUpdate) -> Proveedor:
        """Actualiza un proveedor existente."""
        pass

    @abstractmethod
    def delete_proveedor(self, proveedor_id: int) -> Proveedor:
        """Elimina (soft delete) un proveedor."""
        pass
