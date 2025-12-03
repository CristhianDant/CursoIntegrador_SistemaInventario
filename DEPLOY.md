# 🚀 Guía de Despliegue - Sistema de Inventario

Esta guía te llevará paso a paso para desplegar el sistema en tu VPS de Elástica Perú.

---

## 📋 Prerrequisitos

- VPS con Ubuntu 20.04 o superior
- Acceso SSH al servidor
- Mínimo 2GB RAM, 20GB disco
- Puertos abiertos: 80, 8000, 5432, 9090

---

## 🛠️ Paso 1: Preparar el VPS

### 1.1 Conectar por SSH

```bash
ssh usuario@IP_DE_TU_VPS
```

### 1.2 Actualizar el sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.3 Instalar Docker

```bash
# Descargar script de instalación
curl -fsSL https://get.docker.com -o get-docker.sh

# Ejecutar instalación
sudo sh get-docker.sh

# Agregar usuario al grupo docker (para no usar sudo)
sudo usermod -aG docker $USER

# Aplicar cambios (o cierra sesión y vuelve a entrar)
newgrp docker

# Verificar instalación
docker --version
docker compose version
```

### 1.4 Instalar Git

```bash
sudo apt install git -y
```

---

## 📦 Paso 2: Clonar el Repositorio

```bash
# Ir al directorio home
cd ~

# Clonar el repositorio
git clone https://github.com/CristhianDant/CursoIntegrador_SistemaInventario.git

# Entrar al directorio
cd CursoIntegrador_SistemaInventario
```

---

## ⚙️ Paso 3: Configurar Variables de Entorno

### 3.1 Copiar el archivo de ejemplo

```bash
cp .env.production.example Backent/.env
```

### 3.2 Editar el archivo .env

```bash
nano Backent/.env
```

### 3.3 Configurar valores importantes

Edita estas variables:

```bash
# Base de datos
POST_USER=root
POST_PASS=CambiaEstoPorunPasswordSeguro123!
POST_DB=reposteria_prod
HOST_DB=postgres

# Seguridad - GENERA UNA CLAVE SEGURA
SECRET_KEY=genera-una-clave-super-secreta-aqui-de-64-caracteres-minimo

# Email (configura tu Gmail)
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password_de_gmail

# URL del backend para el frontend
# REEMPLAZA CON LA IP DE TU VPS
VITE_API_BASE_URL=http://TU_IP_VPS:8000/api

# Environment
ENVIRONMENT=production
DEBUG=false
```

**⚠️ IMPORTANTE: Cambia `TU_IP_VPS` por la IP real de tu servidor**

### 3.4 Generar SECRET_KEY segura

```bash
# Generar una clave aleatoria de 64 caracteres
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copia el resultado y pégalo en `SECRET_KEY` en el `.env`

### 3.5 Guardar y salir

Presiona `Ctrl+X`, luego `Y`, luego `Enter`

---

## 🚀 Paso 4: Desplegar la Aplicación

### 4.1 Dar permisos de ejecución al script

```bash
chmod +x deploy.sh
```

### 4.2 Ejecutar el deploy

```bash
./deploy.sh
```

Este script hará:
- ✅ Verificar que Docker está instalado
- ✅ Construir las imágenes Docker
- ✅ Crear la base de datos PostgreSQL
- ✅ Iniciar todos los servicios
- ✅ Ejecutar migraciones de BD
- ✅ Verificar que todo funciona

**Espera 2-3 minutos mientras se construyen las imágenes...**

---

## 🎯 Paso 5: Verificar el Despliegue

### 5.1 Ver el estado de los contenedores

```bash
docker-compose ps
```

Deberías ver 4 servicios corriendo:
- ✅ inventario_postgres
- ✅ inventario_backend
- ✅ inventario_frontend
- ✅ inventario_prometheus

### 5.2 Ver logs en tiempo real

```bash
# Todos los servicios
docker-compose logs -f

# Solo el backend
docker-compose logs -f backend

# Solo el frontend
docker-compose logs -f frontend
```

Presiona `Ctrl+C` para salir de los logs

---

## 🌐 Paso 6: Acceder a la Aplicación

Desde tu navegador, accede a:

- **🖥️ Frontend:** `http://TU_IP_VPS`
- **📡 Backend API:** `http://TU_IP_VPS:8000`
- **📚 Documentación:** `http://TU_IP_VPS:8000/docs`
- **📊 Prometheus:** `http://TU_IP_VPS:9090`

---

## 🔥 Comandos Útiles

### Ver logs
```bash
docker-compose logs -f [servicio]
```

### Reiniciar servicios
```bash
docker-compose restart
```

### Detener todo
```bash
docker-compose down
```

### Iniciar servicios
```bash
docker-compose up -d
```

### Ver uso de recursos
```bash
docker stats
```

### Acceder a un contenedor
```bash
docker-compose exec backend bash
docker-compose exec postgres psql -U root -d reposteria_prod
```

### Backup de la base de datos
```bash
docker-compose exec postgres pg_dump -U root reposteria_prod > backup_$(date +%Y%m%d).sql
```

### Restaurar backup
```bash
cat backup_20241203.sql | docker-compose exec -T postgres psql -U root -d reposteria_prod
```

---

## 🛡️ Configuración de Firewall (Opcional pero Recomendado)

```bash
# Instalar UFW
sudo apt install ufw -y

# Permitir SSH (¡IMPORTANTE!)
sudo ufw allow 22/tcp

# Permitir HTTP
sudo ufw allow 80/tcp

# Permitir backend
sudo ufw allow 8000/tcp

# Permitir Prometheus
sudo ufw allow 9090/tcp

# Activar firewall
sudo ufw enable

# Ver estado
sudo ufw status
```

---

## 🔄 Actualizar la Aplicación

Cuando hagas cambios en el código:

```bash
# Hacer pull de los cambios
git pull origin main

# Rebuilding y reiniciar
./deploy.sh
```

O manualmente:

```bash
# Detener servicios
docker-compose down

# Rebuild
docker-compose build

# Iniciar
docker-compose up -d
```

---

## 🐛 Solución de Problemas

### El backend no inicia

```bash
# Ver logs
docker-compose logs backend

# Verificar variables de entorno
docker-compose exec backend env | grep POST_
```

### Error de conexión a PostgreSQL

```bash
# Verificar que PostgreSQL está corriendo
docker-compose exec postgres pg_isready -U root -d reposteria_prod

# Ver logs de PostgreSQL
docker-compose logs postgres
```

### Frontend no carga

```bash
# Verificar que se construyó correctamente
docker-compose logs frontend

# Reconstruir frontend con la URL correcta
docker-compose build --build-arg VITE_API_BASE_URL=http://TU_IP:8000/api frontend
docker-compose up -d frontend
```

### Puerto 80 ya está en uso

```bash
# Ver qué está usando el puerto
sudo lsof -i :80

# Detener Apache o Nginx si está corriendo
sudo systemctl stop apache2
sudo systemctl stop nginx
```

---

## 📊 Monitoreo

### Ver métricas en Prometheus

1. Accede a `http://TU_IP_VPS:9090`
2. Consultas útiles:
   - `up` - Ver servicios activos
   - `http_requests_total` - Total de requests
   - `http_request_duration_seconds` - Latencia

### Health checks

```bash
# Backend health
curl http://localhost:8000/health

# Backend detailed status
curl http://localhost:8000/status

# Frontend health
curl http://localhost/health
```

---

## 🎉 ¡Listo!

Tu sistema de inventario ya está desplegado y corriendo en producción.

**URLs finales:**
- Frontend: `http://TU_IP_VPS`
- API: `http://TU_IP_VPS:8000`
- Docs: `http://TU_IP_VPS:8000/docs`

**Soporte:**
- GitHub: https://github.com/CristhianDant/CursoIntegrador_SistemaInventario
