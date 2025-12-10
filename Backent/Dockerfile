# ==================== STAGE 1: Builder ====================
FROM python:3.11-slim-bullseye as builder

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ==================== STAGE 2: Runtime ====================
FROM python:3.11-slim-bullseye

WORKDIR /app

# Instalar solo las dependencias runtime necesarias
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar las dependencias instaladas desde el builder
COPY --from=builder /root/.local /root/.local

# Asegurar que los scripts están en el PATH
ENV PATH=/root/.local/bin:$PATH

# Copiar el código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs backups

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
