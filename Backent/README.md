# Proyecto de Inventario con FastAPI

Este es un proyecto de API RESTful construido con FastAPI para gestionar un sistema de inventario.

## Características

*   API RESTful con FastAPI.
*   Base de datos PostgreSQL.
*   Manejo de migraciones con Alembic.
*   Configuración basada en variables de entorno con Pydantic.
*   Autenticación con JWT .

## Requisitos

*   Python 3.9+
*   PostgreSQL
*   pip

## Instalación

1.  **Clona el repositorio:**

    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DEL_DIRECTORIO>
    ```

2.  **Crea un entorno virtual:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instala las dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configura las variables de entorno:**

    Crea un archivo `.env` a partir del ejemplo `.env.example` y rellena los valores correspondientes a tu base de datos.

    ```bash
    cp .env.example .env
    ```

5.  **Crea la base de datos:**

    Asegúrate de que la base de datos especificada en tu archivo `.env` exista en tu servidor PostgreSQL.

6.  **Aplica las migraciones:**

    Para crear las tablas en la base de datos, ejecuta el siguiente comando:

    ```bash
    alembic upgrade head
    ```

## Uso

Para iniciar el servidor de desarrollo, ejecuta:

```bash
uvicorn main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`.

