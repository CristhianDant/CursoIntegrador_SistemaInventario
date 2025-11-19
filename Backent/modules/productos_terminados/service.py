from sqlalchemy.orm import Session
from typing import List, Optional

from modules.productos_terminados.repository import ProductoTerminadoRepository
from modules.productos_terminados.schemas import ProductoTerminado, ProductoTerminadoCreate, ProductoTerminadoUpdate
from modules.productos_terminados.service_interface import ProductoTerminadoServiceInterface


class ProductoTerminadoService(ProductoTerminadoServiceInterface):
    def __init__(self):
        self.repository = ProductoTerminadoRepository()

    def get_all(self, db: Session) -> List[ProductoTerminado]:
        return self.repository.get_all(db)

    def get_by_id(self, db: Session, producto_id: int) -> Optional[ProductoTerminado]:
        return self.repository.get_by_id(db, producto_id)

    def create(self, db: Session, producto: ProductoTerminadoCreate) -> ProductoTerminado:
        # 1. Verificar si el código ya existe
        existing_producto = self.repository.get_by_code(db, producto.codigo_producto)
        if existing_producto:
            raise ValueError(f"El código de producto '{producto.codigo_producto}' ya existe")

        # 2. Validar que stock_minimo sea >= 0
        if producto.stock_minimo is not None and producto.stock_minimo < 0:
            raise ValueError("El stock mínimo debe ser mayor o igual a 0")

        # 3. Capitalizar el nombre del producto - crear una copia modificada
        producto_data = producto.model_dump()
        producto_data['nombre'] = producto_data['nombre'].capitalize()
        producto_modificado = ProductoTerminadoCreate(**producto_data)

        # 4. Crear el producto
        db_producto = self.repository.create(db, producto_modificado)
        return ProductoTerminado.model_validate(db_producto)

    def update(self, db: Session, producto_id: int, producto_update: ProductoTerminadoUpdate) -> Optional[ProductoTerminado]:
        # 1. Validar que stock_minimo sea >= 0
        if producto_update.stock_minimo is not None and producto_update.stock_minimo < 0:
            raise ValueError("El stock mínimo debe ser mayor o igual a 0")

        # 2. Capitalizar el nombre del producto si se proporciona
        producto_data = producto_update.model_dump(exclude_unset=True)
        if 'nombre' in producto_data and producto_data['nombre']:
            producto_data['nombre'] = producto_data['nombre'].capitalize()
            producto_update = ProductoTerminadoUpdate(**producto_data)

        # 3. Actualizar el producto
        db_producto = self.repository.update(db, producto_id, producto_update)
        if db_producto:
            return ProductoTerminado.model_validate(db_producto)
        return None

    def delete(self, db: Session, producto_id: int) -> bool:
        return self.repository.delete(db, producto_id)
