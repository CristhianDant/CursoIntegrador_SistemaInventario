# Pendientes de Implementación - Casos de Uso

Este documento resume los casos de uso que no se cumplen total o parcialmente en la implementación actual del sistema.

### CU-001: Gestionar Cuentas de Usuario

- [ ] **Asignación de Roles:** No existe un mecanismo para asignar roles (Administrador/Empleado) al crear o modificar un usuario. El campo `es_admin` se establece en `False` por defecto y no se puede cambiar a través de la API.
- [ ] **Envío de Correo de Bienvenida:** El sistema no envía un correo electrónico de bienvenida al nuevo usuario con una contraseña temporal.

### CU-002: Iniciar Sesión en el Sistema

- [ ] **Verificación de Usuario Anulado:** La lógica de autenticación no parece verificar si la cuenta del usuario está anulada (`anulado = true`) antes de permitir el inicio de sesión.

### CU-003: Gestionar Catálogo de Insumos

- [ ] **Campos Incompletos:** Al crear un insumo, faltan los campos `codigo`, `stock_minimo` y `categoria` en el esquema `InsumoCreate`.
- [ ] **Stock Inicial:** La lógica para crear un insumo no asegura que el `stock_actual` se inicialice en 0.

### CU-004: Registrar Entrada de Stock (Compra Simple)

- [ ] **Nomenclatura Confusa:** El módulo `ingresos_productos` parece gestionar la entrada de insumos, lo cual es confuso. Debería llamarse `ingresos_insumos` o similar.
- [ ] **Campos Faltantes:** En el esquema para registrar una entrada, faltan campos clave como `precio_unitario` y `fecha_vencimiento` del lote.
- [ ] **Registro de Movimiento:** No está claro si se crea un registro en la tabla `movimiento_insumos` con `tipo_movimiento = 'INGRESO'` después de una entrada de stock.

### CU-005: Registrar Salida por Merma/Desperdicio

- [ ] **Selección de Lote:** El sistema no permite seleccionar un lote específico de insumo para registrar la merma, lo cual es importante para la trazabilidad.
- [ ] **Validación de Stock:** No se valida si la cantidad a mermar es mayor que el stock actual del insumo o del lote.
- [ ] **Registro de Movimiento:** No está claro si se crea un registro en `movimiento_insumos` con `tipo_movimiento = 'MERMA'` tras registrar una merma.

### CU-006: Gestionar Recetas (BOM)

- [ ] **Flujo de Creación:** Aunque se pueden crear recetas y añadirles insumos (detalles), el flujo no sigue exactamente el caso de uso, que sugiere seleccionar primero un producto terminado. La API permite crear la receta directamente. (Observación menor).

### CU-007: Registrar Producción de Producto Terminado

- [ ] **Endpoint Inexistente:** No existe un endpoint o funcionalidad para "Registrar Producción". Este es un caso de uso crítico y está completamente ausente.
- [ ] **Descuento Automático de Insumos:** Como no hay registro de producción, no se implementa el descuento automático de insumos del inventario (`RF-010`).
- [ ] **Incremento de Stock de Producto Terminado:** No se incrementa el stock del producto terminado tras una producción.
- [ ] **Verificación de Stock de Insumos:** No existe la lógica para verificar si hay suficientes insumos antes de confirmar una producción.

### CU-008: Consultar Alertas del Sistema

- [ ] **Endpoint de Alertas:** No hay un endpoint específico en el dashboard o en otro lugar para consultar alertas de stock bajo o caducidad.
- [ ] **Alerta de Stock Bajo:** La lógica para comparar `stock_actual` con `stock_minimo` no está implementada en ninguna parte visible (`RF-011`).
- [ ] **Alerta de Caducidad:** Esta alerta no se puede implementar porque el dato `fecha_vencimiento` no se registra al dar de alta un lote de insumos (ver CU-004) (`RF-012`).

### CU-009: Generar Reporte de Consumo de Insumos

- [ ] **Filtros de Reporte:** El endpoint para obtener movimientos de insumos (`/movimiento_insumos/`) no permite filtrar por rango de fechas, insumo o tipo de movimiento (`CONSUMO_PRODUCCION`), lo cual es esencial para este reporte.
- [ ] **Datos Inexistentes:** El reporte estaría vacío, ya que el movimiento de tipo `CONSUMO_PRODUCCION` nunca se genera (depende del CU-007).

### CU-010: Generar Reporte de Costos de Merma

- [ ] **Filtros de Reporte:** El endpoint de mermas (`/mermas/`) no permite filtrar por rango de fechas o causa, como requiere el caso de uso.
- [ ] **Cálculo de Costo:** El esquema de merma no incluye un campo `costo_total`, por lo que no es posible calcular el impacto financiero de la merma (`RF-014`).

### CU-011: Gestionar Catálogo de Proveedores

- [ ] **Campos Incompletos en Creación/Actualización:** El esquema para la creación y actualización de proveedores (`ProveedorCreate`, `ProveedorUpdate`) no incluye todos los campos mencionados en el caso de uso, como `numero_contacto`, `email_contacto` y `direccion_fiscal`.
- [ ] **Anulación de Proveedor:** El flujo para anular un proveedor no está claramente implementado en el endpoint de actualización.

### CU-012: Gestionar Catálogo de Productos Terminados

- [ ] **Stock Inicial:** La lógica para crear un producto terminado no asegura explícitamente que el `stock_actual` se inicialice en 0.

### CU-013: Generar Orden de Compra (PO)

- [x] **Implementado:** El caso de uso parece estar completamente implementado. Se puede crear una orden de compra con sus detalles y el estado por defecto es 'PENDIENTE'.

### CU-014: Aprobar Orden de Compra

- [ ] **Endpoint Inexistente:** No existe un endpoint específico (ej. `/ordenes/{id}/aprobar`) para aprobar o rechazar una orden de compra. Aunque se podría usar el endpoint `PUT` genérico, no se ajusta al flujo de trabajo descrito y carece de la lógica para asignar el `id_user_aprobador` y la `fecha_aprobacion` automáticamente.

### CU-015: Registrar Ingreso de Stock contra Orden de Compra

- [ ] **Endpoint Inexistente:** No existe un endpoint ni un flujo de trabajo para registrar un ingreso de inventario a partir de una orden de compra aprobada. Este es el vínculo que falta entre el módulo de compras y el de inventario (`ingresos_productos`).
- [ ] **Campos Faltantes:** Como consecuencia de lo anterior, no hay dónde registrar la `fecha_vencimiento` de los lotes que ingresan, lo cual es un requisito funcional (`RF-004`).

### CU-016: Actualizar Costos de Insumos (Costeo)

- [ ] **No Implementado:** Este caso de uso está completamente ausente. No existe una tabla `costo_insumos` ni la lógica para actualizar los costos de los insumos, ya sea de forma automática al ingresar stock o manualmente.

### CU-017: Registrar Salida de Producto Terminado (Venta)

- [ ] **Endpoint Inexistente:** No existe un endpoint para registrar la salida (venta) de un producto terminado. El router de `movimiento_productos_terminados` solo tiene endpoints de consulta (`GET`).
- [ ] **Tipo de Movimiento Faltante:** El `TipoMovimientoEnum` no incluye el valor `VENTA`, por lo que no se podría registrar este tipo de movimiento.

### CU-018: Registrar Merma de Producto Terminado

- [ ] **Lógica Incompleta:** Aunque el esquema de `Merma` permite asociar un `id_producto`, el servicio `MermaService` no implementa la lógica para descontar la cantidad del stock del producto terminado (`productos_terminados.stock_actual`).
- [ ] **Registro de Movimiento Faltante:** El servicio no crea el registro correspondiente en la tabla `movimiento_productos_terminados` con el tipo `MERMA`.

### CU-019: Gestionar Permisos y Roles (Avanzado)

- [ ] **Gestión de Roles Inexistente:** La implementación actual solo permite asignar permisos directamente a los usuarios (`usuario_permisos`). No existe el concepto de "Rol" para agrupar un conjunto de permisos y luego asignarlo a un usuario, que es la base de este caso de uso.
- [ ] **Endpoints Insuficientes:** No hay endpoints para crear, modificar o listar roles.

### CU-020: Configurar Datos de la Empresa

- [x] **Implementado:** Este caso de uso está cubierto. El módulo `empresa` tiene endpoints para crear, obtener y actualizar los datos de la empresa.
