#!/bin/bash

# ==================== Script de Deploy para VPS ====================
# Autor: Sistema de Inventario
# Descripción: Script para desplegar la aplicación en VPS Ubuntu

set -e  # Detener si hay errores

echo "🚀 Iniciando deploy del Sistema de Inventario..."

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ==================== 1. Verificar que .env existe ====================
if [ ! -f "Backent/.env" ]; then
    echo -e "${RED}❌ Error: No se encontró Backent/.env${NC}"
    echo -e "${YELLOW}Copia .env.production.example a Backent/.env y configura tus valores${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Archivo .env encontrado${NC}"

# ==================== 2. Cargar variables de entorno ====================
export $(grep -v '^#' Backent/.env | xargs)

# ==================== 3. Verificar Docker ====================
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    echo "Instala Docker con: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker y Docker Compose disponibles${NC}"

# ==================== 4. Detener contenedores anteriores ====================
echo -e "${YELLOW}🛑 Deteniendo contenedores anteriores...${NC}"
docker-compose down || true

# ==================== 5. Crear red si no existe ====================
docker network create inventario_network 2>/dev/null || true

# ==================== 6. Build de las imágenes ====================
echo -e "${YELLOW}🔨 Construyendo imágenes Docker...${NC}"

# Build del backend
echo "  📦 Backend..."
docker-compose build backend

# Build del frontend con la URL del backend
echo "  📦 Frontend..."
docker-compose build --build-arg VITE_API_BASE_URL="${VITE_API_BASE_URL}" frontend

echo -e "${GREEN}✅ Imágenes construidas${NC}"

# ==================== 7. Iniciar servicios ====================
echo -e "${YELLOW}🚀 Iniciando servicios...${NC}"
docker-compose up -d

# ==================== 8. Esperar a que PostgreSQL esté listo ====================
echo -e "${YELLOW}⏳ Esperando a PostgreSQL...${NC}"
sleep 10

# Verificar que PostgreSQL está corriendo
if docker-compose exec -T postgres pg_isready -U ${POST_USER} -d ${POST_DB} > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL está listo${NC}"
else
    echo -e "${RED}❌ PostgreSQL no responde${NC}"
    docker-compose logs postgres
    exit 1
fi

# ==================== 9. Ejecutar migraciones de Alembic ====================
echo -e "${YELLOW}📊 Ejecutando migraciones de base de datos...${NC}"
docker-compose exec -T backend alembic upgrade head || {
    echo -e "${YELLOW}⚠️  Migraciones no ejecutadas. Verificar si Alembic está configurado.${NC}"
}

# ==================== 10. Verificar que los servicios están corriendo ====================
echo -e "${YELLOW}🔍 Verificando servicios...${NC}"

sleep 5

# Verificar backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend corriendo en http://localhost:8000${NC}"
else
    echo -e "${RED}❌ Backend no responde${NC}"
    docker-compose logs backend
    exit 1
fi

# Verificar frontend
if curl -f http://localhost:80 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend corriendo en http://localhost:80${NC}"
else
    echo -e "${RED}❌ Frontend no responde${NC}"
    docker-compose logs frontend
    exit 1
fi

# Verificar Prometheus
if curl -f http://localhost:9090 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Prometheus corriendo en http://localhost:9090${NC}"
else
    echo -e "${YELLOW}⚠️  Prometheus no responde${NC}"
fi

# ==================== 11. Mostrar logs ====================
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Deploy completado exitosamente!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}📍 URLs de acceso:${NC}"
echo -e "   Frontend:    http://localhost (o http://IP_DE_TU_VPS)"
echo -e "   Backend API: http://localhost:8000 (o http://IP_DE_TU_VPS:8000)"
echo -e "   Docs API:    http://localhost:8000/docs"
echo -e "   Prometheus:  http://localhost:9090"
echo ""
echo -e "${YELLOW}📝 Comandos útiles:${NC}"
echo -e "   Ver logs:           docker-compose logs -f"
echo -e "   Reiniciar:          docker-compose restart"
echo -e "   Detener:            docker-compose down"
echo -e "   Ver estado:         docker-compose ps"
echo -e "   Backup BD:          docker-compose exec postgres pg_dump -U ${POST_USER} ${POST_DB} > backup.sql"
echo ""
echo -e "${GREEN}🎉 Sistema listo para usar!${NC}"
