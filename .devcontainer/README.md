# DevContainer Configuration

This directory contains the configuration for GitHub Codespaces and VS Code DevContainers.

## Services

The configuration sets up three services:

### 1. PostgreSQL Database
- **Image**: `postgres:16-alpine`
- **Port**: 5432
- **Database**: mi_base_de_datos
- **User**: usario
- **Volume**: Persistent storage for database data

### 2. Backend (Python 3.11 + FastAPI)
- **Image**: `python:3.11-slim`
- **Port**: 8000
- **Working Directory**: `/workspace/Backent`
- **Features**:
  - Automatically copies `.env.example` to `.env` if `.env` doesn't exist
  - Installs Python dependencies from `requirements.txt`
  - Runs FastAPI with uvicorn in reload mode
  - Dedicated volume for notifications at `/workspace/Backent/notifications`
  - Auto-connects to PostgreSQL database

### 3. Frontend (Node.js 20 + React + Vite)
- **Image**: `node:20-alpine`
- **Port**: 5173
- **Working Directory**: `/workspace/Frontend`
- **Features**:
  - Automatically installs npm dependencies
  - Runs Vite dev server
  - Separate volume for node_modules to improve performance

## Volumes

- `postgres_data`: Persistent PostgreSQL database storage
- `notifications`: Backend notifications storage
- `frontend_node_modules`: Frontend dependencies cache

## Using This Configuration

### GitHub Codespaces
1. Open the repository in GitHub
2. Click on "Code" → "Codespaces" → "Create codespace on main"
3. Wait for the container to build and start
4. All services will start automatically

### VS Code DevContainers
1. Install the "Dev Containers" extension in VS Code
2. Open the repository in VS Code
3. Press `F1` and select "Dev Containers: Reopen in Container"
4. Wait for the container to build and start

## Port Forwarding

The following ports are automatically forwarded:
- **8000**: Backend FastAPI API (http://localhost:8000)
- **5173**: Frontend React application (http://localhost:5173)
- **5432**: PostgreSQL database (for database clients)

## Environment Variables

Backend environment variables are set in the docker-compose.yml and can be customized by:
1. Modifying `.env.example` in the Backent folder
2. Creating a `.env` file (which is automatically copied from `.env.example`)

## Troubleshooting

If services don't start automatically:
- **Backend**: Run `docker-compose up backend` from the `.devcontainer` directory
- **Frontend**: Run `docker-compose up frontend` from the `.devcontainer` directory
- **Database**: Run `docker-compose up postgres` from the `.devcontainer` directory

To restart all services:
```bash
docker-compose restart
```

To view logs:
```bash
docker-compose logs -f [service-name]
```
