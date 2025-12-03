# 📋 Plan de Mantenimiento del Sistema de Inventario

> **Última actualización:** 3 de diciembre de 2025  
> **Estado:** ✅ Implementado  
> **Módulo:** `modules/backup/` y `jobs/`

---

## 📊 Resumen del Sistema de Mantenimiento

| Componente | Estado | Frecuencia | Descripción |
|------------|--------|------------|-------------|
| Backup Completo | ✅ Activo | Semanal (Lunes 3AM) | Exporta estructura + todos los datos |
| Backup Diferencial | ✅ Activo | Diario (3AM) | Solo cambios desde último backup completo |
| Limpieza Backups | ✅ Activo | Diario | Elimina backups > 90 días |
| Compresión Logs | ✅ Activo | Diario (4AM) | Comprime logs > 7 días |
| Limpieza Logs | ✅ Activo | Diario (4AM) | Elimina logs comprimidos > 90 días |

---

## 🗄️ Sistema de Backups

### Configuración (`config.py`)

```python
# ==================== BACKUP ====================
BACKUP_ENABLED: bool = True              # Habilitar/deshabilitar backups
BACKUP_PATH: str = "backups"             # Directorio de almacenamiento
BACKUP_RETENTION_DAYS: int = 90          # Retención (3 meses)
BACKUP_FULL_DAY: int = 0                 # Día backup completo (0=Lunes)
BACKUP_HOUR: int = 3                     # Hora de ejecución
BACKUP_MINUTE: int = 0
```

### Tipos de Backup

#### 1. Backup Completo (Semanal)
- **Frecuencia:** Cada Lunes a las 3:00 AM
- **Contenido:** Estructura completa + todos los datos de todas las tablas
- **Formato:** `backup_YYYYMMDD_HHMMSS_FULL.sql.gz`
- **Compresión:** gzip
- **Ubicación:** `Backent/backups/`

#### 2. Backup Diferencial (Diario)
- **Frecuencia:** Todos los días excepto Lunes a las 3:00 AM
- **Contenido:** Solo registros modificados desde el último backup completo
- **Formato:** `backup_YYYYMMDD_HHMMSS_DIFF.sql.gz`
- **Referencia:** Usa campos de auditoría (`fecha_creacion`, `fecha_actualizacion`)

### Política de Retención

```
┌─────────────────────────────────────────────────────────────┐
│                    CICLO DE RETENCIÓN                       │
├─────────────────────────────────────────────────────────────┤
│  Día 0-90: ✅ Backups almacenados y disponibles             │
│  Día 90+:  🗑️ Eliminación automática (job diario)           │
└─────────────────────────────────────────────────────────────┘
```

### Endpoints API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/backup/estadisticas` | Estadísticas del sistema de backups |
| GET | `/api/v1/backup/listar` | Lista todos los backups disponibles |
| GET | `/api/v1/backup/{id}` | Información de un backup específico |
| POST | `/api/v1/backup/ejecutar` | Ejecutar backup manual |
| POST | `/api/v1/backup/ejecutar-completo` | Atajo para backup completo |
| POST | `/api/v1/backup/ejecutar-diferencial` | Atajo para backup diferencial |
| GET | `/api/v1/backup/{id}/descargar` | Descargar archivo de backup |
| POST | `/api/v1/backup/{id}/enviar-email` | Enviar backup por email |
| POST | `/api/v1/backup/limpiar` | Limpiar backups antiguos manualmente |

### Ejemplo de Uso

#### Ejecutar Backup Manual
```bash
curl -X POST "http://localhost:8000/api/v1/backup/ejecutar-completo?usuario=admin"
```

#### Descargar Backup
```bash
curl -O "http://localhost:8000/api/v1/backup/1/descargar"
```

#### Enviar por Email
```bash
curl -X POST "http://localhost:8000/api/v1/backup/1/enviar-email" \
  -H "Content-Type: application/json" \
  -d '{"id_backup": 1, "email_destino": "admin@empresa.com"}'
```

---

## 📝 Sistema de Mantenimiento de Logs

### Configuración (`config.py`)

```python
# ==================== LOGS MAINTENANCE ====================
LOGS_COMPRESSION_ENABLED: bool = True    # Habilitar compresión
LOGS_COMPRESSION_DAYS: int = 7           # Comprimir después de 7 días
LOGS_RETENTION_DAYS: int = 90            # Eliminar después de 90 días
LOGS_PATH: str = "logs"                  # Directorio de logs
```

### Archivos de Log Actuales

| Archivo | Descripción | Rotación | Retención |
|---------|-------------|----------|-----------|
| `app.log` | Logs generales | 10 MB | 7 días |
| `error.log` | Solo errores | 1 día | 10 días |
| `health.log` | Health checks | 1 día | 14 días |
| `sesiones.log` | Inicio de sesión | 1 día | 30 días |

### Flujo de Mantenimiento

```
┌─────────────────────────────────────────────────────────────┐
│                  CICLO DE VIDA DE LOGS                      │
├─────────────────────────────────────────────────────────────┤
│  Día 0-7:   📄 Logs activos (sin comprimir)                 │
│  Día 7-90:  📦 Logs comprimidos (.gz)                       │
│  Día 90+:   🗑️ Eliminación automática                       │
└─────────────────────────────────────────────────────────────┘
```

---

## ⏰ Programación de Jobs (Scheduler)

### Jobs Registrados

| Job ID | Nombre | Hora | Descripción |
|--------|--------|------|-------------|
| `alertas_diarias` | Alertas diarias | 06:00 | Generar alertas vencimiento/stock |
| `backup_diario` | Backup BD | 03:00 | Backup completo (Lunes) o diferencial |
| `logs_maintenance` | Mantenimiento logs | 04:00 | Comprimir y limpiar logs |

### Diagrama de Ejecución Diaria

```
00:00 ─────┬───────────────────────────────────────────────── 24:00
           │
     03:00 ├── 📦 Backup (FULL si Lunes, DIFF otros días)
           │   └── 🧹 Limpieza backups > 90 días
           │
     04:00 ├── 📦 Compresión logs > 7 días
           │   └── 🗑️ Eliminar logs.gz > 90 días
           │
     06:00 └── ⚠️ Alertas vencimiento y stock
```

---

## 🗄️ Modelo de Datos

### Tabla: `historial_backup`

```sql
CREATE TABLE historial_backup (
    id_backup BIGSERIAL PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL,           -- COMPLETO, DIFERENCIAL
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo TEXT NOT NULL,
    tamanio_bytes BIGINT,
    tamanio_legible VARCHAR(50),
    estado VARCHAR(20) DEFAULT 'COMPLETADO', -- EN_PROCESO, COMPLETADO, ERROR
    mensaje_error TEXT,
    duracion_segundos FLOAT,
    tablas_respaldadas BIGINT,
    registros_totales BIGINT,
    hash_md5 VARCHAR(32),
    id_backup_base BIGINT,               -- FK para diferenciales
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    fecha_eliminacion TIMESTAMP WITH TIME ZONE,
    eliminado BOOLEAN DEFAULT FALSE,
    ejecutado_por VARCHAR(100)           -- SCHEDULER, MANUAL, usuario
);
```

### Notificaciones de Backup

Los eventos de backup generan notificaciones en la tabla `notificaciones`:

```python
# Backup exitoso
tipo = "BACKUP"
titulo = "✅ Backup COMPLETO completado"
semaforo = "VERDE"

# Backup fallido
tipo = "BACKUP"
titulo = "❌ Error en Backup COMPLETO"
semaforo = "ROJO"
```

---

## 🔧 Restauración de Backups

### Descomprimir Archivo

```bash
# Descomprimir backup
gunzip backup_20251203_030000_FULL.sql.gz

# O mantener el original
gunzip -k backup_20251203_030000_FULL.sql.gz
```

### Restaurar en PostgreSQL

```bash
# Conectar al contenedor de PostgreSQL
docker exec -i postgres_container psql -U usuario -d base_datos < backup_20251203_030000_FULL.sql

# O directamente
psql -h localhost -U usuario -d base_datos < backup_20251203_030000_FULL.sql
```

### Restaurar Backup Diferencial

1. Primero restaurar el backup completo base
2. Luego aplicar el backup diferencial

```bash
# 1. Restaurar backup completo
psql -U usuario -d base_datos < backup_20251201_030000_FULL.sql

# 2. Aplicar diferencial (usa UPSERT)
psql -U usuario -d base_datos < backup_20251203_030000_DIFF.sql
```

---

## 📊 Monitoreo

### Métricas de Backup

Verificar estado del sistema:

```bash
curl http://localhost:8000/api/v1/backup/estadisticas
```

Respuesta ejemplo:
```json
{
    "total_backups": 15,
    "backups_completos": 3,
    "backups_diferenciales": 12,
    "espacio_usado_bytes": 157286400,
    "espacio_usado_legible": "150.00 MB",
    "ultimo_backup_completo": "2025-12-02T03:00:00Z",
    "ultimo_backup_diferencial": "2025-12-03T03:00:00Z",
    "dias_retencion": 90
}
```

### Health Check

El endpoint `/health` incluye verificación de:
- Base de datos
- Scheduler (jobs de backup activos)
- Espacio en disco para backups

---

## 🚨 Solución de Problemas

### Backup Fallido

1. Revisar logs: `logs/app.log`
2. Verificar espacio en disco: `df -h`
3. Verificar conexión a BD: `curl http://localhost:8000/health`
4. Ejecutar backup manual para ver error detallado

### Logs No se Comprimen

1. Verificar configuración: `LOGS_COMPRESSION_ENABLED=True`
2. Verificar permisos del directorio `logs/`
3. Verificar que el job esté registrado: revisar logs del scheduler

### Espacio en Disco Lleno

```bash
# Ver espacio usado por backups
du -sh backups/

# Limpiar backups antiguos manualmente
curl -X POST http://localhost:8000/api/v1/backup/limpiar

# Limpiar logs comprimidos
find logs/ -name "*.gz" -mtime +90 -delete
```

---

## 📁 Estructura de Archivos

```
Backent/
├── backups/                          # Directorio de backups
│   ├── .gitkeep
│   ├── backup_20251201_030000_FULL.sql.gz
│   └── backup_20251202_030000_DIFF.sql.gz
├── logs/                             # Directorio de logs
│   ├── app.log
│   ├── error.log
│   ├── health.log
│   ├── sesiones.log
│   └── app.log.2025-11-25.gz         # Logs comprimidos
├── jobs/
│   ├── alertas_job.py
│   ├── backup_job.py                 # ✅ Nuevo
│   └── logs_maintenance_job.py       # ✅ Nuevo
├── modules/
│   └── backup/                       # ✅ Nuevo módulo
│       ├── __init__.py
│       ├── model.py
│       ├── schemas.py
│       ├── service.py
│       └── router.py
└── alembic/versions/
    └── f837844d0006_crear_tabla_historial_backup.py
```

---

## ✅ Checklist de Implementación

- [x] Crear módulo `modules/backup/`
- [x] Crear modelo `HistorialBackup`
- [x] Implementar `BackupService` con SQLAlchemy
- [x] Crear endpoints REST
- [x] Implementar backup completo semanal
- [x] Implementar backup diferencial diario
- [x] Limpieza automática (90 días)
- [x] Compresión con gzip
- [x] Verificación MD5
- [x] Registro en tabla de notificaciones
- [x] Job de mantenimiento de logs
- [x] Documentación
- [x] Migración Alembic
