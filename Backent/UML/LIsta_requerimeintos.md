# 📋 Requisitos Pendientes del Sistema de Inventario

> **Fecha de evaluación:** 28 de noviembre de 2025  
> **Completitud actual:** ~35%  
> **Basado en:** Estándares de tesis (Kumar et al., 2021; Najlae et al., 2021; Meza Hernández, 2024)

---
aaaaaaaa
## 📊 Resumen de Estado

| Categoría | Implementado | Pendiente | % Completitud |
|-----------|--------------|-----------|---------------|
| Funciones Core (8) | 2 | 6 | 25% |
| Indicadores KPI (5) | 0.5 | 4.5 | 10% |
| Módulos Pantalla (4) | 1 | 3 | 25% |
| Pruebas de Software y Seguridad | 0 | 5 | 0% |
| Despliegue del Proyecto | 0 | 4 | 0% |
| Monitoreo del Proyecto | 0 | 4 | 0% |
| Mantenimiento del Proyecto | 0 | 4 | 0% |
| **TOTAL** | - | - | **~25%** |

---

## ❌ Requisitos No Cumplidos

### 🎯 FUNCIONES CORE

| ID | Requisito | Prioridad | Estado | Módulo Afectado |
|----|-----------|-----------|--------|-----------------|
| FC-01 | Salidas por producción (descuento automático FEFO) | 🔴 Alta | Parcial | `produccion/` |
| FC-02 | Ventas con descuento automático de stock | 🔴 Alta | No existe | `ventas/` |
| FC-03 | Semáforo de vencimientos (Verde/Amarillo/Rojo) | 🔴 Alta | No existe | `alertas/` |
| FC-04 | Lista diaria "Usar hoy" | 🟡 Media | No existe | `alertas/` |
| FC-05 | Alertas automáticas de stock crítico | 🔴 Alta | No existe | `alertas/` |
| FC-06 | Alertas de vencimiento próximo | 🔴 Alta | No existe | `alertas/` |
| FC-07 | Análisis ABC de productos | 🟡 Media | No existe | `reportes/` |
| FC-08 | Punto de Venta integrado | 🔴 Alta | No existe | `ventas/` |
| FC-09 | Descuento automático productos día anterior | 🟡 Media | No existe | `ventas/` |
| FC-10 | Lista de compras automática | 🟡 Media | No existe | `compras/` |
| FC-11 | Costeo automático de recetas | 🟡 Media | Parcial | `recetas/` |
| FC-12 | Reporte diario automático | 🟡 Media | No existe | `reportes/` |

### 📊 INDICADORES KPI

| ID | Requisito | Prioridad | Estado | Módulo Afectado |
|----|-----------|-----------|--------|-----------------|
| KPI-01 | Cálculo % merma diaria | 🔴 Alta | No existe | `dashboard/` |
| KPI-02 | Contador productos vencidos hoy | 🔴 Alta | No existe | `dashboard/` |
| KPI-03 | Métrica cumplimiento FEFO | 🟡 Media | No existe | `dashboard/` |
| KPI-04 | Contador stock crítico | 🔴 Alta | No existe | `dashboard/` |
| KPI-05 | Cálculo rotación inventario | 🟢 Baja | No existe | `dashboard/` |

### 🖥️ PANTALLAS/MÓDULOS

| ID | Requisito | Prioridad | Estado | Módulo Afectado |
|----|-----------|-----------|--------|-----------------|
| PM-01 | Dashboard con KPIs | 🔴 Alta | No existe | `dashboard/` |
| PM-02 | Pantalla de Producción sugerida | 🟡 Media | Parcial | `produccion/` |
| PM-03 | Punto de Venta (POS) | 🔴 Alta | No existe | `ventas/` |
| PM-04 | Inventario con semáforo visual | 🟡 Media | Parcial | `alertas/` |

### 🧪 PRUEBAS DE SOFTWARE Y SEGURIDAD (Rúbrica: 60-70%)

| ID | Requisito | Prioridad | Estado | Descripción |
|----|-----------|-----------|--------|-------------|
| TEST-01 | Tests unitarios | 🔴 Alta | No existe | Tests para services y repositories con pytest |
| TEST-02 | Tests de integración | 🔴 Alta | No existe | Tests de endpoints API con TestClient |
| TEST-03 | Tests de seguridad | 🔴 Alta | No existe | Pruebas de autenticación, autorización, SQL injection, XSS |
| TEST-04 | Reporte de cobertura | 🟡 Media | No existe | Cobertura mínima 70% con pytest-cov |
| TEST-05 | Reporte de pruebas de seguridad | 🔴 Alta | No existe | Documento con vulnerabilidades encontradas y mitigaciones |

### 🚀 DESPLIEGUE DEL PROYECTO (Rúbrica: 80%)

| ID | Requisito | Prioridad | Estado | Descripción |
|----|-----------|-----------|--------|-------------|
| DEP-01 | Dockerfile | 🔴 Alta | No existe | Containerización de la aplicación |
| DEP-02 | Docker Compose | 🔴 Alta | No existe | Orquestación de servicios (app + db + redis) |
| DEP-03 | CI/CD Pipeline | 🟡 Media | No existe | GitHub Actions para build, test y deploy automático |
| DEP-04 | Documentación de despliegue | 🟡 Media | No existe | Guía paso a paso para desplegar en servidor |

### 📊 MONITOREO DEL PROYECTO (Rúbrica: 90%)

| ID | Requisito | Prioridad | Estado | Descripción |
|----|-----------|-----------|--------|-------------|
| MON-01 | Sistema de logs estructurados | 🔴 Alta | Parcial | Logs con formato JSON, niveles y rotación |
| MON-02 | Métricas de rendimiento | 🟡 Media | No existe | Tiempos de respuesta, uso de recursos |
| MON-03 | Health checks | 🔴 Alta | No existe | Endpoints /health y /ready para verificar estado |
| MON-04 | Plan de monitoreo | 🟡 Media | No existe | Documento con estrategia de monitoreo y alertas |

### 🔧 MANTENIMIENTO DEL PROYECTO (Rúbrica: 100%)

| ID | Requisito | Prioridad | Estado | Descripción |
|----|-----------|-----------|--------|-------------|
| MAN-01 | Scripts de backup | 🔴 Alta | No existe | Backup automático de base de datos |
| MAN-02 | Cron jobs | 🟡 Media | No existe | Tareas programadas (limpieza, reportes, alertas) |
| MAN-03 | Scripts de mantenimiento | 🟡 Media | No existe | Limpieza de logs, optimización de BD |
| MAN-04 | Plan de mantenimiento | 🔴 Alta | No existe | Documento con procedimientos de mantenimiento |

### 📦 CONSTRUCCIÓN DEL PRODUCTO FINAL (Rúbrica)

| ID | Criterio | Prioridad | Estado | Descripción |
|----|----------|-----------|--------|-------------|
| PRD-01 | Completitud (alcance comprometido) | 🔴 Alta | Parcial | Cubrir todas las funcionalidades del alcance |
| PRD-02 | Coherencia (documentación vs código) | 🔴 Alta | Parcial | Documentación alineada con implementación |
| PRD-03 | Buenas prácticas | 🟡 Media | Parcial | Patrones de diseño, librerías adecuadas, Git |
| PRD-04 | Autoría (dominio del código) | 🔴 Alta | ✅ Cumple | Código desarrollado y dominado por el estudiante |

---

## 📝 Descripción Detallada de Implementación

---

### FC-01: Salidas por Producción con Descuento Automático FEFO

**Estado:** 🟡 Parcial  
**Prioridad:** 🔴 Alta  
**Módulo:** `gestion_almacen_inusmos/produccion/`

#### Descripción
Al ejecutar una producción basada en una receta, el sistema debe descontar automáticamente los insumos necesarios siguiendo el principio FEFO (First Expired, First Out), priorizando los lotes que vencen primero.

#### Implementación Requerida

```python
# Archivos a crear/modificar:
# 1. produccion/model.py - Modelo de datos
# 2. produccion/service.py - Lógica de negocio
# 3. produccion/router.py - Endpoints API
```

**Modelo de datos:**
```python
class Produccion(Base):
    __tablename__ = "produccion"
    
    id: int                    # PK
    receta_id: int             # FK -> recetas.id
    cantidad_producida: float  # Unidades producidas
    fecha_produccion: datetime
    usuario_id: int            # FK -> usuarios.id
    observaciones: str

class ProduccionDetalleConsumo(Base):
    """Trazabilidad de lotes consumidos"""
    __tablename__ = "produccion_detalle_consumo"
    
    id: int
    produccion_id: int         # FK -> produccion.id
    ingreso_insumo_id: int     # FK -> ingreso_producto.id (lote)
    cantidad_consumida: float
```

**Endpoints requeridos:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/produccion/validar` | Valida stock disponible para receta |
| POST | `/produccion/ejecutar` | Ejecuta producción y descuenta insumos |
| GET | `/produccion/historial` | Lista producciones realizadas |
| GET | `/produccion/{id}/trazabilidad` | Muestra lotes usados en producción |

**Flujo de ejecución:**
```
1. Recibir: receta_id, cantidad_a_producir
2. Obtener detalles de receta (insumos necesarios)
3. Por cada insumo:
   a. Calcular cantidad_necesaria = cantidad_receta × cantidad_a_producir
   b. Obtener lotes FEFO (ordenados por fecha_vencimiento ASC)
   c. Descontar de lotes hasta cubrir cantidad_necesaria
   d. Registrar en ProduccionDetalleConsumo
4. Crear registro de Produccion
5. Incrementar stock de producto_terminado
6. Retornar resumen con trazabilidad
```

**Dependencias:** 
- `ingresos_insumos/service.py` (get_lotes_fefo)
- `recetas/service.py` (get_detalle_receta)
- `movimiento_insumos/service.py` (registrar_salida)

---

### FC-02: Ventas con Descuento Automático de Stock

**Estado:** ❌ No existe  
**Prioridad:** 🔴 Alta  
**Módulo:** `ventas/` (nuevo)

#### Descripción
Sistema de Punto de Venta que al registrar una venta, descuente automáticamente del inventario de productos terminados en tiempo real.

#### Implementación Requerida

**Estructura de archivos:**
```
modules/ventas/
├── __init__.py
├── model.py
├── schemas.py
├── repository.py
├── repository_interface.py
├── service.py
├── service_interface.py
└── router.py
```

**Modelo de datos:**
```python
class Venta(Base):
    __tablename__ = "ventas"
    
    id: int
    fecha: datetime
    total: float
    metodo_pago: str           # efectivo, tarjeta, yape, plin
    usuario_id: int            # FK -> usuarios.id
    estado: str                # completada, anulada

class VentaDetalle(Base):
    __tablename__ = "venta_detalles"
    
    id: int
    venta_id: int              # FK -> ventas.id
    producto_terminado_id: int # FK -> productos_terminados.id
    cantidad: int
    precio_unitario: float
    descuento_porcentaje: float
    subtotal: float
```

**Endpoints requeridos:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/ventas/registrar` | Registra venta y descuenta stock |
| GET | `/ventas/del-dia` | Ventas del día actual |
| GET | `/ventas/{id}` | Detalle de una venta |
| POST | `/ventas/{id}/anular` | Anula venta y restaura stock |
| GET | `/ventas/productos-disponibles` | Lista productos con stock para vender |

**Flujo de venta:**
```
1. Recibir: lista de items [{producto_id, cantidad, precio}]
2. Validar stock disponible para cada producto
3. Calcular totales con descuentos
4. Crear registro Venta + VentaDetalles
5. Por cada item: descontar de productos_terminados
6. Retornar ticket/comprobante
```

---

### FC-03: Semáforo de Vencimientos

**Estado:** ❌ No existe  
**Prioridad:** 🔴 Alta  
**Módulo:** `alertas/` (nuevo)

#### Descripción
Clasificación visual de insumos según proximidad a fecha de vencimiento:
- 🟢 **Verde:** >15 días de vida útil
- 🟡 **Amarillo:** 7-15 días → USAR ESTA SEMANA
- 🔴 **Rojo:** <7 días → USAR HOY/PRIORIDAD

#### Implementación Requerida

**Estructura de archivos:**
```
modules/alertas/
├── __init__.py
├── schemas.py
├── service.py
└── router.py
```

**Schemas:**
```python
class InsumoConSemaforo(BaseModel):
    insumo_id: int
    nombre: str
    lote: str
    cantidad_disponible: float
    fecha_vencimiento: date
    dias_restantes: int
    semaforo: str              # "verde", "amarillo", "rojo"
    accion_sugerida: str       # "Normal", "Usar esta semana", "Usar hoy"

class ResumenSemaforo(BaseModel):
    total_verde: int
    total_amarillo: int
    total_rojo: int
    items_rojo: List[InsumoConSemaforo]
    items_amarillo: List[InsumoConSemaforo]
```

**Endpoints requeridos:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/alertas/semaforo` | Resumen de semáforo completo |
| GET | `/alertas/semaforo/rojo` | Solo items críticos (<7 días) |
| GET | `/alertas/semaforo/amarillo` | Items de atención (7-15 días) |
| GET | `/alertas/usar-hoy` | Lista de insumos a usar hoy (FEFO) |

**Lógica de clasificación:**
```python
def clasificar_semaforo(fecha_vencimiento: date) -> dict:
    hoy = date.today()
    dias_restantes = (fecha_vencimiento - hoy).days
    
    if dias_restantes < 0:
        return {"semaforo": "vencido", "accion": "DESECHAR"}
    elif dias_restantes < 7:
        return {"semaforo": "rojo", "accion": "Usar HOY"}
    elif dias_restantes <= 15:
        return {"semaforo": "amarillo", "accion": "Usar esta semana"}
    else:
        return {"semaforo": "verde", "accion": "Normal"}
```

---

### FC-04: Lista Diaria "Usar Hoy"

**Estado:** ❌ No existe  
**Prioridad:** 🟡 Media  
**Módulo:** `alertas/`

#### Descripción
Genera automáticamente cada día una lista priorizada de insumos que deben usarse ese día para evitar pérdidas por vencimiento.

#### Implementación Requerida

**Endpoint:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/alertas/usar-hoy` | Lista FEFO de items a usar hoy |

**Response Schema:**
```python
class UsarHoyResponse(BaseModel):
    fecha: date
    total_items: int
    valor_en_riesgo: float     # Suma del valor de items que vencen
    items: List[ItemUsarHoy]

class ItemUsarHoy(BaseModel):
    insumo_id: int
    nombre: str
    lote: str
    cantidad: float
    unidad_medida: str
    fecha_vencimiento: date
    dias_restantes: int
    valor_estimado: float
    recetas_sugeridas: List[str]  # Recetas donde puede usarse
```

**Lógica:**
```python
def obtener_usar_hoy(db: Session) -> UsarHoyResponse:
    # 1. Obtener todos los lotes que vencen en <= 3 días
    # 2. Ordenar por fecha_vencimiento ASC (FEFO)
    # 3. Calcular valor en riesgo
    # 4. Sugerir recetas donde pueden usarse
    # 5. Retornar lista priorizada
```

---

### FC-05: Alertas Automáticas de Stock Crítico

**Estado:** ❌ No existe  
**Prioridad:** 🔴 Alta  
**Módulo:** `alertas/`

#### Descripción
Sistema que detecta cuando el stock actual de un insumo está por debajo del stock mínimo configurado y genera alertas.

#### Implementación Requerida

**Endpoint:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/alertas/stock-critico` | Lista insumos bajo mínimo |
| GET | `/alertas/stock-critico/dias-produccion` | Stock expresado en días de producción |

**Response Schema:**
```python
class AlertaStockCritico(BaseModel):
    insumo_id: int
    nombre: str
    stock_actual: float
    stock_minimo: float
    unidad_medida: str
    deficit: float             # stock_minimo - stock_actual
    dias_produccion: float     # Stock actual / consumo_diario_promedio
    urgencia: str              # "critico", "bajo", "normal"
    proveedor_sugerido: str
    ultimo_precio: float

class ResumenStockCritico(BaseModel):
    total_criticos: int        # stock_actual = 0
    total_bajos: int           # stock_actual < stock_minimo
    valor_compra_sugerida: float
    items: List[AlertaStockCritico]
```

**Lógica de clasificación:**
```python
def clasificar_stock(stock_actual: float, stock_minimo: float) -> str:
    if stock_actual == 0:
        return "critico"       # ⚠️ SIN STOCK
    elif stock_actual < stock_minimo:
        return "bajo"          # 🟡 Comprar pronto
    elif stock_actual < stock_minimo * 1.5:
        return "atencion"      # Monitorear
    else:
        return "normal"        # ✅ OK
```

---

### FC-06: Alertas de Vencimiento Próximo

**Estado:** ❌ No existe  
**Prioridad:** 🔴 Alta  
**Módulo:** `alertas/`

#### Descripción
Notificaciones automáticas cuando insumos están próximos a vencer.

#### Implementación Requerida

**Endpoint:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/alertas/vencimientos` | Lista vencimientos próximos |
| GET | `/alertas/vencimientos?dias=7` | Filtrar por días |
| GET | `/alertas/vencen-manana` | Específico para mañana |

**Response Schema:**
```python
class AlertaVencimiento(BaseModel):
    insumo_id: int
    nombre: str
    lote: str
    cantidad: float
    unidad_medida: str
    fecha_vencimiento: date
    dias_restantes: int
    valor_en_riesgo: float
    mensaje: str               # "X kg de harina vence mañana"

class ResumenVencimientos(BaseModel):
    vencen_hoy: List[AlertaVencimiento]
    vencen_manana: List[AlertaVencimiento]
    vencen_esta_semana: List[AlertaVencimiento]
    valor_total_en_riesgo: float
```

---

### FC-07: Análisis ABC de Productos

**Estado:** ❌ No existe  
**Prioridad:** 🟡 Media  
**Módulo:** `reportes/` (nuevo)

#### Descripción
Clasificación de productos según su contribución a las ventas:
- **Categoría A (70% ventas):** Control DIARIO
- **Categoría B (20% ventas):** Control SEMANAL
- **Categoría C (10% ventas):** Control MENSUAL

#### Implementación Requerida

**Estructura de archivos:**
```
modules/reportes/
├── __init__.py
├── schemas.py
├── service.py
└── router.py
```

**Endpoint:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/reportes/analisis-abc` | Clasificación ABC completa |
| GET | `/reportes/analisis-abc/categoria/{cat}` | Filtrar por A, B o C |

**Response Schema:**
```python
class ProductoABC(BaseModel):
    producto_id: int
    nombre: str
    ventas_periodo: float
    porcentaje_ventas: float
    porcentaje_acumulado: float
    categoria: str             # "A", "B", "C"
    frecuencia_revision: str   # "diario", "semanal", "mensual"

class AnalisisABC(BaseModel):
    periodo_analisis: str      # "Últimos 30 días"
    categoria_a: List[ProductoABC]
    categoria_b: List[ProductoABC]
    categoria_c: List[ProductoABC]
    resumen: dict
```

**Algoritmo:**
```python
def calcular_abc(ventas: List) -> dict:
    # 1. Ordenar productos por ventas DESC
    # 2. Calcular % de cada producto sobre total
    # 3. Calcular % acumulado
    # 4. Asignar categoría:
    #    - A: hasta 70% acumulado
    #    - B: 70-90% acumulado
    #    - C: 90-100% acumulado
```

---

### FC-08: Punto de Venta Integrado

**Estado:** ❌ No existe  
**Prioridad:** 🔴 Alta  
**Módulo:** `ventas/`

#### Descripción
Interfaz de caja registradora que permite:
- Seleccionar productos rápidamente
- Aplicar descuentos
- Procesar múltiples métodos de pago
- Descontar automáticamente del inventario
- Generar ticket de venta

#### Implementación Requerida

Ver **FC-02** para modelo de datos.

**Endpoints adicionales para POS:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/ventas/pos/productos` | Productos con precio y stock para POS |
| GET | `/ventas/pos/productos-descuento` | Productos del día anterior con descuento |
| POST | `/ventas/pos/ticket` | Genera ticket imprimible |
| GET | `/ventas/pos/caja-del-dia` | Resumen de caja |
| POST | `/ventas/pos/cerrar-caja` | Cierre de caja diario |

**Schema para POS:**
```python
class ProductoPOS(BaseModel):
    id: int
    nombre: str
    precio: float
    stock_disponible: int
    es_del_dia_anterior: bool
    descuento_sugerido: float  # 30-50% si es del día anterior
    precio_con_descuento: float

class CierreCaja(BaseModel):
    fecha: date
    total_ventas: float
    cantidad_transacciones: int
    efectivo: float
    tarjeta: float
    otros: float
    diferencia: float          # Efectivo esperado vs contado
```

---

### FC-09: Descuento Automático Productos Día Anterior

**Estado:** ❌ No existe  
**Prioridad:** 🟡 Media  
**Módulo:** `ventas/`

#### Descripción
El sistema identifica automáticamente productos terminados producidos el día anterior y sugiere/aplica descuento del 30-50%.

#### Implementación Requerida

**Endpoint:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/ventas/productos-descuento` | Lista productos con descuento sugerido |
| PUT | `/ventas/aplicar-descuento-masivo` | Aplica descuento a productos antiguos |

**Lógica:**
```python
def obtener_productos_descuento(db: Session) -> List:
    hoy = date.today()
    ayer = hoy - timedelta(days=1)
    
    # Obtener productos producidos ayer que aún tienen stock
    productos_ayer = db.query(ProductoTerminado)\
        .filter(ProductoTerminado.fecha_produccion < hoy)\
        .filter(ProductoTerminado.stock > 0)\
        .all()
    
    for producto in productos_ayer:
        dias_antiguedad = (hoy - producto.fecha_produccion).days
        if dias_antiguedad == 1:
            descuento = 0.30  # 30%
        elif dias_antiguedad == 2:
            descuento = 0.50  # 50%
        else:
            descuento = 0.70  # 70% o marcar como merma
        
        producto.descuento_sugerido = descuento
    
    return productos_ayer
```

---

### FC-10: Lista de Compras Automática

**Estado:** ❌ No existe  
**Prioridad:** 🟡 Media  
**Módulo:** `compras/` (nuevo) o `orden_de_compra/`

#### Descripción
Genera semanalmente una lista de compras sugerida basada en:
- Consumo promedio histórico
- Stock actual
- Próximos vencimientos
- Lead time del proveedor
- Stock de seguridad

#### Implementación Requerida

**Endpoint:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/compras/sugerencia-semanal` | Lista de compras sugerida |
| POST | `/compras/generar-orden` | Convierte sugerencia en orden de compra |

**Response Schema:**
```python
class SugerenciaCompra(BaseModel):
    insumo_id: int
    nombre: str
    stock_actual: float
    consumo_promedio_diario: float
    dias_stock_restante: float
    cantidad_sugerida: float
    unidad_medida: str
    proveedor_sugerido: str
    precio_estimado: float
    urgencia: str              # "inmediata", "esta_semana", "proxima_semana"
    razon: str                 # "Stock bajo", "Vencimiento próximo", etc.

class ListaComprasSemanal(BaseModel):
    semana: str
    fecha_generacion: datetime
    total_estimado: float
    items: List[SugerenciaCompra]
```

**Algoritmo:**
```python
def generar_lista_compras(db: Session, dias_proyeccion: int = 7):
    insumos = obtener_todos_insumos(db)
    sugerencias = []
    
    for insumo in insumos:
        consumo_diario = calcular_consumo_promedio(db, insumo.id, dias=30)
        stock_actual = obtener_stock_actual(db, insumo.id)
        dias_restantes = stock_actual / consumo_diario if consumo_diario > 0 else float('inf')
        
        # Si quedan menos días que el lead_time + stock_seguridad
        if dias_restantes < (insumo.lead_time_dias + insumo.stock_seguridad_dias):
            cantidad_sugerida = consumo_diario * dias_proyeccion
            sugerencias.append(SugerenciaCompra(
                insumo_id=insumo.id,
                cantidad_sugerida=cantidad_sugerida,
                # ...
            ))
    
    return sugerencias
```

---

### FC-11: Costeo Automático de Recetas

**Estado:** 🟡 Parcial  
**Prioridad:** 🟡 Media  
**Módulo:** `recetas/`

#### Descripción
Calcular automáticamente el costo de producción de cada receta basado en los precios actuales de los insumos, y sugerir precio de venta con margen.

#### Implementación Requerida

**Endpoints adicionales en recetas:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/recetas/{id}/costeo` | Costeo detallado de una receta |
| GET | `/recetas/{id}/precio-sugerido?margen=60` | Precio con margen |
| GET | `/recetas/rentabilidad` | Ranking de recetas por rentabilidad |

**Response Schema:**
```python
class CosteoReceta(BaseModel):
    receta_id: int
    nombre_receta: str
    cantidad_producida: int    # Ej: 100 panes
    
    detalles: List[CosteoDetalle]
    
    costo_total: float
    costo_unitario: float
    precio_venta_actual: float
    margen_actual: float       # (precio - costo) / precio × 100
    precio_sugerido: float     # Con margen objetivo
    ganancia_por_unidad: float

class CosteoDetalle(BaseModel):
    insumo_id: int
    nombre_insumo: str
    cantidad_necesaria: float
    unidad_medida: str
    precio_unitario: float     # Precio actual del insumo
    subtotal: float
```

**Lógica:**
```python
def calcular_costeo(receta_id: int, db: Session) -> CosteoReceta:
    receta = obtener_receta(db, receta_id)
    costo_total = 0
    detalles = []
    
    for detalle in receta.detalles:
        insumo = obtener_insumo(db, detalle.insumo_id)
        precio_insumo = obtener_ultimo_precio(db, insumo.id)
        subtotal = detalle.cantidad * precio_insumo
        costo_total += subtotal
        
        detalles.append(CosteoDetalle(
            insumo_id=insumo.id,
            nombre_insumo=insumo.nombre,
            cantidad_necesaria=detalle.cantidad,
            precio_unitario=precio_insumo,
            subtotal=subtotal
        ))
    
    costo_unitario = costo_total / receta.cantidad_producida
    margen_objetivo = 0.60  # 60%
    precio_sugerido = costo_unitario / (1 - margen_objetivo)
    
    return CosteoReceta(
        costo_total=costo_total,
        costo_unitario=costo_unitario,
        precio_sugerido=precio_sugerido,
        detalles=detalles
    )
```

---

### FC-12: Reporte Diario Automático

**Estado:** ❌ No existe  
**Prioridad:** 🟡 Media  
**Módulo:** `reportes/`

#### Descripción
Genera automáticamente al cierre del día un reporte con:
- Ventas del día
- % de merma (META: <3%)
- Productos que vencen mañana
- Stock crítico

#### Implementación Requerida

**Endpoint:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/reportes/diario` | Reporte del día actual |
| GET | `/reportes/diario/{fecha}` | Reporte de fecha específica |
| POST | `/reportes/generar-cierre` | Genera y guarda reporte de cierre |

**Response Schema:**
```python
class ReporteDiario(BaseModel):
    fecha: date
    
    # Ventas
    ventas_total: float
    ventas_cantidad: int
    ticket_promedio: float
    
    # Mermas
    merma_kg: float
    merma_valor: float
    merma_porcentaje: float
    merma_meta: float          # 3%
    merma_cumple: bool
    
    # Vencimientos
    vencen_manana: List[AlertaVencimiento]
    valor_en_riesgo: float
    
    # Stock
    stock_critico: List[AlertaStockCritico]
    
    # Producción
    produccion_total: int
    recetas_producidas: List[dict]
    
    # Indicadores
    cumplimiento_fefo: float
    productos_vendidos_top5: List[dict]
```

---

### KPI-01: Cálculo % Merma Diaria

**Estado:** ❌ No existe  
**Prioridad:** 🔴 Alta  
**Módulo:** `dashboard/` (nuevo)

#### Descripción
Calcular y mostrar el porcentaje de merma diaria.  
**Fórmula:** `% Merma = (kg perdidos / kg totales) × 100`  
**Meta:** < 3%

#### Implementación Requerida

**Endpoint:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/dashboard/kpi/merma-diaria` | % merma del día |
| GET | `/dashboard/kpi/merma-historico?dias=30` | Tendencia de mermas |

**Lógica:**
```python
def calcular_merma_diaria(db: Session, fecha: date) -> dict:
    # Obtener mermas del día
    mermas = db.query(Merma).filter(
        func.date(Merma.fecha) == fecha
    ).all()
    
    kg_perdidos = sum(m.cantidad for m in mermas)
    
    # Obtener total de kg manejados (entradas + stock inicial)
    kg_totales = obtener_kg_totales_dia(db, fecha)
    
    porcentaje = (kg_perdidos / kg_totales * 100) if kg_totales > 0 else 0
    
    return {
        "fecha": fecha,
        "kg_perdidos": kg_perdidos,
        "kg_totales": kg_totales,
        "porcentaje": round(porcentaje, 2),
        "meta": 3.0,
        "cumple_meta": porcentaje < 3.0,
        "estado": "✅" if porcentaje < 3.0 else "❌"
    }
```

---

### KPI-02: Contador Productos Vencidos Hoy

**Estado:** ❌ No existe  
**Prioridad:** 🔴 Alta  
**Módulo:** `dashboard/`

#### Descripción
Contar cuántos productos/lotes vencieron hoy.  
**Meta:** 0 productos vencidos

#### Implementación Requerida

**Endpoint:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/dashboard/kpi/vencidos-hoy` | Contador de vencidos |

**Lógica:**
```python
def contar_vencidos_hoy(db: Session) -> dict:
    hoy = date.today()
    
    vencidos = db.query(IngresoProducto).filter(
        IngresoProducto.fecha_vencimiento <= hoy,
        IngresoProducto.cantidad_disponible > 0
    ).all()
    
    return {
        "fecha": hoy,
        "cantidad_lotes": len(vencidos),
        "cantidad_kg": sum(v.cantidad_disponible for v in vencidos),
        "valor_perdido": calcular_valor(vencidos),
        "meta": 0,
        "cumple_meta": len(vencidos) == 0,
        "detalle": [{"insumo": v.insumo.nombre, "lote": v.lote} for v in vencidos]
    }
```

---

### KPI-03: Métrica Cumplimiento FEFO

**Estado:** ❌ No existe  
**Prioridad:** 🟡 Media  
**Módulo:** `dashboard/`

#### Descripción
Medir si las salidas de inventario siguen el principio FEFO.  
**Fórmula:** `Cumplimiento FEFO = (Salidas FEFO / Total salidas) × 100`  
**Meta:** > 95%

#### Implementación Requerida

**Endpoint:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/dashboard/kpi/cumplimiento-fefo` | % cumplimiento FEFO |

**Lógica:**
```python
def calcular_cumplimiento_fefo(db: Session, dias: int = 30) -> dict:
    fecha_inicio = date.today() - timedelta(days=dias)
    
    # Obtener todos los movimientos de salida
    salidas = db.query(MovimientoInsumo).filter(
        MovimientoInsumo.tipo == "SALIDA",
        MovimientoInsumo.fecha >= fecha_inicio
    ).all()
    
    salidas_fefo = 0
    total_salidas = len(salidas)
    
    for salida in salidas:
        # Verificar si se usó el lote que vencía primero
        if es_salida_fefo(db, salida):
            salidas_fefo += 1
    
    porcentaje = (salidas_fefo / total_salidas * 100) if total_salidas > 0 else 100
    
    return {
        "periodo": f"Últimos {dias} días",
        "salidas_fefo": salidas_fefo,
        "total_salidas": total_salidas,
        "porcentaje": round(porcentaje, 2),
        "meta": 95.0,
        "cumple_meta": porcentaje >= 95.0
    }
```

---

### KPI-04: Contador Stock Crítico

**Estado:** ❌ No existe  
**Prioridad:** 🔴 Alta  
**Módulo:** `dashboard/`

#### Descripción
Contar cuántos insumos tienen stock por debajo del mínimo.  
**Meta:** < 3 productos en stock crítico

#### Implementación Requerida

**Endpoint:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/dashboard/kpi/stock-critico` | Contador de stock crítico |

**Lógica:**
```python
def contar_stock_critico(db: Session) -> dict:
    insumos = db.query(Insumo).all()
    criticos = []
    
    for insumo in insumos:
        stock_actual = calcular_stock_actual(db, insumo.id)
        if stock_actual < insumo.stock_minimo:
            criticos.append({
                "insumo": insumo.nombre,
                "stock_actual": stock_actual,
                "stock_minimo": insumo.stock_minimo,
                "deficit": insumo.stock_minimo - stock_actual
            })
    
    return {
        "cantidad": len(criticos),
        "meta": 3,
        "cumple_meta": len(criticos) < 3,
        "items": criticos
    }
```

---

### KPI-05: Cálculo Rotación de Inventario

**Estado:** ❌ No existe  
**Prioridad:** 🟢 Baja  
**Módulo:** `dashboard/`

#### Descripción
Medir cuántas veces se renueva el inventario en un año.  
**Fórmula:** `Rotación = Costo de ventas / Inventario promedio`  
**Meta:** > 12 veces/año

#### Implementación Requerida

**Endpoint:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/dashboard/kpi/rotacion-inventario` | Rotación anualizada |

**Lógica:**
```python
def calcular_rotacion(db: Session) -> dict:
    # Costo de ventas del último mes
    costo_ventas_mes = calcular_costo_ventas(db, dias=30)
    
    # Inventario promedio
    inventario_promedio = calcular_inventario_promedio(db, dias=30)
    
    # Rotación mensual
    rotacion_mensual = costo_ventas_mes / inventario_promedio if inventario_promedio > 0 else 0
    
    # Anualizar
    rotacion_anual = rotacion_mensual * 12
    
    return {
        "rotacion_mensual": round(rotacion_mensual, 2),
        "rotacion_anual": round(rotacion_anual, 2),
        "meta_anual": 12.0,
        "cumple_meta": rotacion_anual >= 12.0,
        "interpretacion": "Alta rotación = buena gestión" if rotacion_anual >= 12 else "Baja rotación = revisar"
    }
```

---

### PM-01: Dashboard con KPIs

**Estado:** ❌ No existe  
**Prioridad:** 🔴 Alta  
**Módulo:** `dashboard/` (nuevo)

#### Descripción
Pantalla principal que muestra resumen del día con todos los KPIs críticos.

#### Implementación Requerida

**Estructura de archivos:**
```
modules/dashboard/
├── __init__.py
├── schemas.py
├── service.py
└── router.py
```

**Endpoint principal:**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/dashboard` | Dashboard completo |
| GET | `/dashboard/kpis` | Solo los 5 KPIs |
| GET | `/dashboard/alertas` | Resumen de alertas |

**Response Schema:**
```python
class Dashboard(BaseModel):
    fecha: date
    
    # KPIs
    kpis: DashboardKPIs
    
    # Alertas
    alertas_criticas: int
    alertas: List[Alerta]
    
    # Usar esta semana
    usar_esta_semana: List[InsumoConSemaforo]
    
    # Resumen ventas
    ventas_hoy: float
    meta_ventas: float
    porcentaje_meta: float

class DashboardKPIs(BaseModel):
    merma_diaria: KPIValue
    productos_vencidos: KPIValue
    cumplimiento_fefo: KPIValue
    stock_critico: KPIValue
    rotacion_inventario: KPIValue

class KPIValue(BaseModel):
    valor: float
    meta: float
    unidad: str
    cumple: bool
    tendencia: str             # "subiendo", "bajando", "estable"
```

---

## 📅 Cronograma Sugerido de Implementación

| Fase | Duración | Módulos | Prioridad |
|------|----------|---------|-----------|
| **Fase 1** | 2 semanas | Completar `produccion/` + `dashboard/` básico | 🔴 Alta |
| **Fase 2** | 2 semanas | `alertas/` completo + semáforo vencimientos | 🔴 Alta |
| **Fase 3** | 2 semanas | `ventas/` (POS) + descuentos automáticos | 🔴 Alta |
| **Fase 4** | 1 semana | `reportes/` + análisis ABC | 🟡 Media |
| **Fase 5** | 1 semana | Costeo recetas + lista compras automática | 🟡 Media |
| **Fase 6** | 1 semana | Refinamiento KPIs + optimización | 🟢 Baja |
| **Fase 7** | 2 semanas | Tests unitarios + integración + seguridad (60-70%) | 🔴 Alta |
| **Fase 8** | 1 semana | Despliegue: Docker + CI/CD (80%) | 🔴 Alta |
| **Fase 9** | 1 semana | Monitoreo: Logs + Health checks + Plan (90%) | 🔴 Alta |
| **Fase 10** | 1 semana | Mantenimiento: Backups + Cron + Plan (100%) | 🔴 Alta |

**Total estimado:** 14 semanas para completar al 100%

---

## 📋 Mapeo de Rúbrica Universitaria

| Criterio Rúbrica | % Requerido | Estado Actual | IDs Relacionados |
|------------------|-------------|---------------|------------------|
| Pruebas de Software y Seguridad | 60-70% | 0% | TEST-01 a TEST-05 |
| Despliegue del Proyecto | 80% | 0% | DEP-01 a DEP-04 |
| Monitoreo del Proyecto | 90% | 10% | MON-01 a MON-04 |
| Mantenimiento del Proyecto | 100% | 0% | MAN-01 a MAN-04 |
| Construcción del Producto Final | 100% | 50% | PRD-01 a PRD-04 |

---

## 📚 Referencias

- Kumar et al. (2021) - Meta de mermas 3%
- Najlae et al. (2021) - Sistema FEFO
- Meza Hernández (2024) - Alertas automáticas
- Don Mamino/Agro Luz - Clasificación ABC