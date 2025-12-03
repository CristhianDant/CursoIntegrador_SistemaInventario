# 🍰 Sistema de Gestión de Inventario para Repostería

Sistema web completo para gestión de inventario, producción y ventas de una repostería artesanal. Desarrollado con FastAPI (Backend) y React + Vite (Frontend).

---

## 📊 Características Principales

### ✅ Gestión de Inventario
- Control de insumos con lotes FEFO (First Expired, First Out)
- Gestión de productos terminados
- Alertas de stock bajo y vencimientos próximos
- Semáforo de estados (Verde/Amarillo/Rojo)

### 🏭 Producción
- Recetas con costeo automático
- Descuento automático de insumos en producción
- Trazabilidad completa de lotes consumidos
- Historial de producción

### 💰 Ventas (POS)
- Punto de venta integrado
- Descuento automático de productos del día anterior
- Historial de ventas
- Reportes diarios

### 📈 Reportes y Métricas
- Dashboard con KPIs en tiempo real
- % de merma diaria (META: <3%)
- Cumplimiento FEFO (META: >95%)
- Análisis ABC de productos

### 🔔 Alertas Automáticas
- Stock crítico
- Vencimientos próximos
- Lista "Usar Hoy"
- Envío automático por email

---

## 🛠️ Tecnologías

**Backend:** FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT, Pytest
**Frontend:** React 18, Vite, Radix UI, Tailwind CSS
**DevOps:** Docker, Docker Compose, Nginx, Prometheus

---

## 🚀 Despliegue Rápido

```bash
# 1. Clonar
git clone https://github.com/CristhianDant/CursoIntegrador_SistemaInventario.git
cd CursoIntegrador_SistemaInventario

# 2. Configurar
cp .env.production.example Backent/.env
nano Backent/.env  # Editar configuración

# 3. Deploy
chmod +x deploy.sh
./deploy.sh
```

**📖 Guía completa:** [DEPLOY.md](DEPLOY.md)

---

## 📁 Estructura

```
├── Backent/          # FastAPI + PostgreSQL
│   ├── modules/      # Módulos de negocio
│   ├── Dockerfile
│   └── main.py
├── Frontend/         # React + Vite
│   ├── src/
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── deploy.sh
```

---

## 🌐 URLs (Producción)

- Frontend: `http://TU_IP_VPS`
- API: `http://TU_IP_VPS:8000`
- Docs: `http://TU_IP_VPS:8000/docs`
- Prometheus: `http://TU_IP_VPS:9090`

---

## 🧪 Testing

```bash
pytest                    # Todos los tests
pytest --cov             # Con cobertura (74.94%)
```

---

## 📧 Contacto

**GitHub:** [@CristhianDant](https://github.com/CristhianDant)
