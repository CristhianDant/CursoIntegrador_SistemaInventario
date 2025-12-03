from sqlalchemy.orm import Session
from decimal import Decimal
from modules.insumo.repository import InsumoRepository
from modules.insumo.schemas import Insumo, InsumoCreate, InsumoUpdate
from .service_interface import InsumoServiceInterface


class InsumoService(InsumoServiceInterface):
    def __init__(self, db: Session):
        self.repository = InsumoRepository(db)

    def create_insumo(self, insumo: InsumoCreate) -> Insumo:
        # 1. Verificar si el código ya existe
        existing_insumo = self.repository.get_inusmo_cod(insumo.codigo)
        if existing_insumo:
            raise ValueError(f"El código de insumo '{insumo.codigo}' ya existe")

        # 2. Validar que stock_minimo sea >= 0
        if insumo.stock_minimo is not None and insumo.stock_minimo < 0:
            raise ValueError("El stock mínimo debe ser mayor o igual a 0")

        # 3. Capitalizar el nombre del insumo - crear una copia modificada
        insumo_data = insumo.model_dump()
        insumo_data['nombre'] = insumo_data['nombre'].capitalize()
        insumo_modificado = InsumoCreate(**insumo_data)

        # 4. Crear el insumo
        db_insumo = self.repository.create_insumo(insumo_modificado)
        return Insumo.model_validate(db_insumo)

    def get_insumos(self, skip: int = 0, limit: int = 100) -> list[Insumo]:
        insumos = self.repository.get_insumos(skip, limit)
        
        # Obtener stocks y precios calculados
        stocks = self.repository.get_stock_actual_por_insumo()
        precios = self.repository.get_precio_promedio_por_insumo()
        
        # Agregar campos calculados a cada insumo
        resultado = []
        for insumo in insumos:
            insumo_dict = {
                'id_insumo': insumo.id_insumo,
                'codigo': insumo.codigo,
                'nombre': insumo.nombre,
                'descripcion': insumo.descripcion,
                'unidad_medida': insumo.unidad_medida,
                'stock_minimo': insumo.stock_minimo,
                'perecible': insumo.perecible,
                'categoria': insumo.categoria,
                'fecha_registro': insumo.fecha_registro,
                'anulado': insumo.anulado,
                'stock_actual': stocks.get(insumo.id_insumo, Decimal('0')),
                'precio_promedio': precios.get(insumo.id_insumo, Decimal('0'))
            }
            resultado.append(Insumo(**insumo_dict))
        
        return resultado

    def get_insumo(self, insumo_id: int) -> Insumo | None:
        db_insumo = self.repository.get_insumo(insumo_id)
        if db_insumo:
            # Obtener stocks y precios calculados
            stocks = self.repository.get_stock_actual_por_insumo()
            precios = self.repository.get_precio_promedio_por_insumo()
            
            insumo_dict = {
                'id_insumo': db_insumo.id_insumo,
                'codigo': db_insumo.codigo,
                'nombre': db_insumo.nombre,
                'descripcion': db_insumo.descripcion,
                'unidad_medida': db_insumo.unidad_medida,
                'stock_minimo': db_insumo.stock_minimo,
                'perecible': db_insumo.perecible,
                'categoria': db_insumo.categoria,
                'fecha_registro': db_insumo.fecha_registro,
                'anulado': db_insumo.anulado,
                'stock_actual': stocks.get(db_insumo.id_insumo, Decimal('0')),
                'precio_promedio': precios.get(db_insumo.id_insumo, Decimal('0'))
            }
            return Insumo(**insumo_dict)
        return None

    def update_insumo(self, insumo_id: int, insumo: InsumoUpdate) -> Insumo | None:
        # 1. Validar que stock_minimo sea >= 0
        if insumo.stock_minimo is not None and insumo.stock_minimo < 0:
            raise ValueError("El stock mínimo debe ser mayor o igual a 0")

        # 2. Capitalizar el nombre del insumo si se proporciona
        insumo_data = insumo.model_dump(exclude_unset=True)
        if 'nombre' in insumo_data and insumo_data['nombre']:
            insumo_data['nombre'] = insumo_data['nombre'].capitalize()
            insumo = InsumoUpdate(**insumo_data)

        # 3. Actualizar el insumo
        db_insumo = self.repository.update_insumo(insumo_id, insumo)
        if db_insumo:
            return Insumo.model_validate(db_insumo)
        return None

    def delete_insumo(self, insumo_id: int) -> Insumo | None:
        db_insumo = self.repository.delete_insumo(insumo_id)
        if db_insumo:
            return Insumo.model_validate(db_insumo)
        return None

    def get_ultimos_precios(self) -> dict:
        """Obtiene el último precio de compra de cada insumo."""
        return self.repository.get_ultimos_precios()
