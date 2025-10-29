-- Inserción de permisos generales para cada módulo
INSERT INTO "permisos" (descripcion_permiso, modulo, accion) VALUES
('general para empresa', 'empresa', 'general'),
('general para usuario', 'usuario', 'general'),
('general para permisos', 'permisos', 'general'),
('general para proveedores', 'proveedores', 'general'),
('general para insumo', 'insumo', 'general'),
('general para costo_insumos', 'costo_insumos', 'general'),
('general para orden_de_compra', 'orden_de_compra', 'general'),
('general para ingresos_productos', 'ingresos_productos', 'general'),
('general para recetas', 'recetas', 'general'),
('general para productos_terminados', 'productos_terminados', 'general'),
('general para movimiento_insumos', 'movimiento_insumos', 'general'),
('general para movimiento_productos_terminados', 'movimiento_productos_terminados', 'general'),
('general para calidad_desperdicio_merma', 'calidad_desperdicio_merma', 'general');

-- Inserción del usuario administrador
INSERT INTO "usuario" (es_admin, nombre, apellidos, email, password) VALUES
(true, 'administrador', 'admin', 'admin@email.com', '$pbkdf2-sha256$29000$MaaUEiJEqHVurfVe633PuQ$t2qfT4BIuKXVuJGR/Em7XwepeZayJtpHUstcVUlva18');

-- Asignación de todos los permisos al usuario administrador
INSERT INTO "usuario_permisos" (id_user, id_permiso)
SELECT 
    (SELECT id_user FROM "usuario" WHERE email = 'admin@email.com'),
    p.id_permiso
FROM "permisos" p;