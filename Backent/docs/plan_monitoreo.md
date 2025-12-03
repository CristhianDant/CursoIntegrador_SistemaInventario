# 📊 Plan de Monitoreo del Sistema de Inventario

> **Versión:** 1.0  
> **Fecha:** 3 de diciembre de 2025  
> **Autor:** Equipo de Desarrollo  
> **Estado:** Implementado

---

## 📋 Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura de Monitoreo](#arquitectura-de-monitoreo)
3. [Componentes Monitoreados](#componentes-monitoreados)
4. [Métricas y KPIs](#métricas-y-kpis)
5. [Sistema de Alertas](#sistema-de-alertas)
6. [Endpoints de Monitoreo](#endpoints-de-monitoreo)
7. [Configuración](#configuración)
8. [Procedimientos de Respuesta](#procedimientos-de-respuesta)
9. [Logs y Trazabilidad](#logs-y-trazabilidad)

---

## 📝 Resumen Ejecutivo

Este documento describe la estrategia de monitoreo implementada para el Sistema de Inventario. El sistema utiliza:

- **Prometheus + FastAPI Instrumentator** para métricas de rendimiento
- **Loguru** para logging estructurado con soporte JSON
- **Health Checks** con endpoints `/health`, `/ready` y `/status`
- **Sistema de Alertas** integrado con notificaciones por email

### Objetivos del Monitoreo

| Objetivo | Métrica | Meta |
|----------|---------|------|
| Disponibilidad | Uptime | > 99.5% |
| Latencia | Tiempo de respuesta P95 | < 500ms |
| Errores | Tasa de errores 5xx | < 1% |
| Base de datos | Tiempo de query | < 100ms |

---

## 🏗️ Arquitectura de Monitoreo

```
┌─────────────────────────────────────────────────────────────────┐
│                    Sistema de Inventario                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   FastAPI    │───▶│  Prometheus  │───▶│   Grafana    │      │
│  │    App       │    │ Instrumentator│    │  (opcional)  │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Loguru     │───▶│  Log Files   │───▶│   ELK/Loki   │      │
│  │   Logger     │    │  (JSON/Text) │    │  (opcional)  │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Health     │───▶│   Alert      │───▶│    Email     │      │
│  │   Service    │    │   Service    │    │   Service    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Componentes Monitoreados

### 1. Base de Datos (PostgreSQL)

| Verificación | Frecuencia | Umbral Amarillo | Umbral Rojo |
|--------------|------------|-----------------|-------------|
| Conectividad | Cada request | N/A | Sin conexión |
| Tiempo de respuesta | Cada request | > 100ms | > 500ms |
| Pool de conexiones | 1 minuto | > 80% usado | > 95% usado |

### 2. Scheduler (APScheduler)

| Verificación | Frecuencia | Umbral Amarillo | Umbral Rojo |
|--------------|------------|-----------------|-------------|
| Estado del scheduler | 1 minuto | Deshabilitado | No corriendo |
| Ejecución de jobs | Por evento | Retraso > 1hr | Job fallido |
| Próxima ejecución | 1 minuto | > 24hr | Sin programar |

### 3. Servicios Externos

| Servicio | Verificación | Umbral |
|----------|--------------|--------|
| SMTP (Gmail) | Configuración | Credenciales ausentes |
| Storage (Logs) | Espacio disco | < 10% libre |

### 4. Aplicación

| Métrica | Umbral Amarillo | Umbral Rojo |
|---------|-----------------|-------------|
| CPU | > 70% | > 90% |
| Memoria | > 80% | > 95% |
| Requests en progreso | > 100 | > 200 |

---

## 📈 Métricas y KPIs

### Métricas de Prometheus (Endpoint: `/metrics`)

```prometheus
# Latencia de requests (histograma)
http_request_duration_seconds_bucket{handler="/api/v1/...", method="GET", le="0.1"}

# Conteo de requests
http_requests_total{handler="/api/v1/...", method="GET", status="200"}

# Requests en progreso
http_requests_inprogress{handler="/api/v1/..."}

# Tamaño de requests/responses
http_request_size_bytes_sum
http_response_size_bytes_sum
```

### KPIs del Negocio (Endpoint: `/api/v1/reportes/kpis`)

| KPI | Descripción | Meta | Frecuencia |
|-----|-------------|------|------------|
| Merma diaria | % productos perdidos | < 3% | Diaria |
| Productos vencidos | Lotes vencidos hoy | 0 | Diaria |
| Cumplimiento FEFO | % salidas correctas | > 95% | Semanal |
| Stock crítico | Insumos bajo mínimo | < 3 | Diaria |
| Rotación inventario | Veces/año | > 12 | Mensual |

---

## 🚨 Sistema de Alertas

### Niveles de Severidad

| Nivel | Color | Acción | Tiempo de Respuesta |
|-------|-------|--------|---------------------|
| CRITICAL | 🔴 | Email + Notificación BD | Inmediato |
| HIGH | 🟠 | Notificación BD | < 1 hora |
| MEDIUM | 🟡 | Log + Notificación BD | < 4 horas |
| INFO | 🟢 | Solo Log | N/A |

### Reglas de Escalamiento

```python
# Lógica de escalamiento implementada en alert_service.py

1. Primer fallo: Severidad HIGH
2. 3+ fallos consecutivos: Severidad CRITICAL + Email
3. Recuperación: Notificación INFO
```

### Canales de Notificación

| Canal | Alertas | Configuración |
|-------|---------|---------------|
| Email | CRITICAL | SMTP_USER, SMTP_PASSWORD |
| Base de Datos | ALL | Tabla `notificaciones` |
| Logs | ALL | logs/health.log |

---

## 🔌 Endpoints de Monitoreo

### Health Checks

| Endpoint | Método | Descripción | Uso |
|----------|--------|-------------|-----|
| `/health` | GET | Liveness probe | Kubernetes liveness |
| `/ready` | GET | Readiness probe | Kubernetes readiness |
| `/status` | GET | Estado detallado | Diagnóstico manual |
| `/ping` | GET | Ping simple | Load balancer |
| `/health/check-and-alert` | POST | Verificar y alertar | Monitoreo manual |

### Métricas

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/metrics` | GET | Métricas Prometheus |

### Ejemplos de Respuesta

#### GET /health
```json
{
  "status": "healthy",
  "timestamp": "2025-12-03T10:30:00Z",
  "version": "1.0.0",
  "uptime_seconds": 3600.5
}
```

#### GET /ready
```json
{
  "status": "healthy",
  "timestamp": "2025-12-03T10:30:00Z",
  "version": "1.0.0",
  "uptime_seconds": 3600.5,
  "components": [
    {
      "name": "database",
      "status": "healthy",
      "response_time_ms": 15.2,
      "message": "Database connection is healthy"
    },
    {
      "name": "scheduler",
      "status": "healthy",
      "message": "Scheduler running with 1 jobs"
    },
    {
      "name": "smtp",
      "status": "degraded",
      "message": "SMTP credentials not configured"
    }
  ],
  "total_components": 3,
  "healthy_components": 2,
  "degraded_components": 1,
  "unhealthy_components": 0
}
```

---

## ⚙️ Configuración

### Variables de Entorno

```env
# ==================== SCHEDULER ====================
SCHEDULER_ENABLED=true
SCHEDULER_HORA_DEFAULT=6
SCHEDULER_MINUTO_DEFAULT=0
SCHEDULER_TIMEZONE=America/Lima

# ==================== LOGGING ====================
LOG_LEVEL=INFO
LOG_FORMAT=text          # text para desarrollo, json para producción
LOG_FILE_ROTATION=10 MB
LOG_FILE_RETENTION=10 days

# ==================== MONITOREO ====================
ENABLE_METRICS=true
METRICS_PATH=/metrics

# Umbrales de health checks
DB_RESPONSE_TIME_WARNING_MS=100
DB_RESPONSE_TIME_CRITICAL_MS=500

# Alertas de salud
HEALTH_CHECK_ALERT_ENABLED=true
HEALTH_CHECK_INTERVAL_SECONDS=60

# ==================== ENVIRONMENT ====================
ENVIRONMENT=development   # development, staging, production
DEBUG=true
APP_VERSION=1.0.0
```

### Configuración de Prometheus (prometheus.yml)

```yaml
# Para integración con Prometheus server externo

global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'inventario-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

---

## 📋 Procedimientos de Respuesta

### Procedimiento: Base de Datos No Disponible

```
🔴 ALERTA: database - UNHEALTHY

1. VERIFICAR conexión de red al servidor PostgreSQL
   $ ping <HOST_DB>

2. VERIFICAR que PostgreSQL está corriendo
   $ sudo systemctl status postgresql
   $ docker ps | grep postgres  # si usa Docker

3. VERIFICAR credenciales en .env
   - POST_USER, POST_PASS, POST_DB, POST_PORT, HOST_DB

4. VERIFICAR logs de PostgreSQL
   $ sudo tail -f /var/log/postgresql/postgresql-*.log

5. REINICIAR servicio si es necesario
   $ sudo systemctl restart postgresql

6. VERIFICAR recuperación
   $ curl http://localhost:8000/ready
```

### Procedimiento: Scheduler No Corriendo

```
🔴 ALERTA: scheduler - UNHEALTHY

1. VERIFICAR configuración
   - SCHEDULER_ENABLED=true en .env

2. VERIFICAR logs de la aplicación
   $ tail -f logs/app.log | grep -i scheduler

3. REINICIAR aplicación
   $ sudo systemctl restart inventario-api
   # o
   $ docker-compose restart api

4. VERIFICAR jobs programados
   $ curl http://localhost:8000/status | jq '.scheduler_info'
```

### Procedimiento: Alta Latencia

```
🟡 ALERTA: Latencia > 500ms

1. VERIFICAR métricas de Prometheus
   $ curl http://localhost:8000/metrics | grep http_request_duration

2. IDENTIFICAR endpoints lentos
   - Revisar logs/app.log para requests con alto tiempo

3. VERIFICAR uso de recursos
   $ curl http://localhost:8000/status | jq '.system_info'

4. ACCIONES POSIBLES:
   - Optimizar queries lentas
   - Agregar índices a la BD
   - Escalar horizontalmente (más instancias)
   - Agregar caché
```

---

## 📝 Logs y Trazabilidad

### Archivos de Log

| Archivo | Contenido | Rotación | Retención |
|---------|-----------|----------|-----------|
| `logs/app.log` | Todos los logs | Diaria | 7 días |
| `logs/error.log` | Solo errores | 10 MB | 10 días |
| `logs/sesiones.log` | Login/Logout | Diaria | 30 días |
| `logs/health.log` | Health checks | Diaria | 14 días |

### Formato de Logs

#### Desarrollo (text)
```
2025-12-03 10:30:00 | INFO     | [a1b2c3d4] main:lifespan:45 - ✅ Aplicación iniciada
```

#### Producción (json)
```json
{
  "timestamp": "2025-12-03T10:30:00.123Z",
  "level": "INFO",
  "message": "✅ Aplicación iniciada",
  "logger": "main",
  "function": "lifespan",
  "line": 45,
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "environment": "production",
  "version": "1.0.0"
}
```

### Trazabilidad con Request ID

Cada request incluye un `X-Request-ID` que:
- Se genera automáticamente si no viene en el request
- Se propaga en todos los logs durante el request
- Se incluye en el header de respuesta
- Permite correlacionar logs de un mismo request

---

## 📊 Dashboard Recomendado (Grafana)

### Paneles Sugeridos

1. **Disponibilidad**
   - Uptime de los últimos 7 días
   - Estado actual de componentes

2. **Latencia**
   - Histograma de tiempos de respuesta
   - P50, P95, P99 por endpoint

3. **Tráfico**
   - Requests por segundo
   - Distribución por método HTTP
   - Top 10 endpoints

4. **Errores**
   - Tasa de errores 4xx y 5xx
   - Errores por endpoint

5. **Recursos**
   - CPU y memoria
   - Conexiones a BD
   - Espacio en disco

---

## 🔄 Mantenimiento del Monitoreo

### Tareas Periódicas

| Tarea | Frecuencia | Responsable |
|-------|------------|-------------|
| Revisar alertas activas | Diaria | DevOps |
| Limpiar logs antiguos | Automático | Sistema |
| Actualizar umbrales | Mensual | DevOps |
| Revisar métricas de rendimiento | Semanal | Desarrollo |
| Backup de configuración | Semanal | DevOps |

### Checklist de Revisión Semanal

- [ ] Verificar que todos los componentes están healthy
- [ ] Revisar tendencias de latencia
- [ ] Analizar errores de la semana
- [ ] Verificar espacio en disco para logs
- [ ] Confirmar que el scheduler ejecuta jobs correctamente
- [ ] Revisar alertas enviadas y su resolución

---

## 📚 Referencias

- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [FastAPI Performance](https://fastapi.tiangolo.com/deployment/)
- [Loguru Documentation](https://loguru.readthedocs.io/)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
