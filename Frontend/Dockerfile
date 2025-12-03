# ==================== STAGE 1: Build ====================
FROM node:20-alpine as builder

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY . .

# Argument para la URL del backend (se pasa en build time)
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Build de producción
RUN npm run build

# ==================== STAGE 2: Nginx Server ====================
FROM nginx:alpine

# Copiar el build de Vite
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuración de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Comando por defecto
CMD ["nginx", "-g", "daemon off;"]
