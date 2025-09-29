from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import your settings and Base
import os
import sys
from database import Base
from config import settings


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))



config = context.config


database_url = f"postgresql://{settings.POST_USER}:{settings.POST_PASS}@localhost:{settings.POST_PORT}/{settings.POST_DB}"
config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata




def run_migrations_offline() -> None:
    """Ejecuta las migraciones en modo 'offline'.

    Esto configura el contexto solo con una URL
    y no un motor, aunque un motor también es aceptable
    aquí. Al omitir la creación del motor,
    ni siquiera necesitamos que una DBAPI esté disponible.

    Las llamadas a context.execute() aquí emiten la cadena dada a la
    salida del script.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta las migraciones en modo 'online'.

    En este escenario, necesitamos crear un motor
    y asociar una conexión con el contexto.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
