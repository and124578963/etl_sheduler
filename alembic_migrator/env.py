import os
from logging.config import fileConfig

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
from common.config_controller import Config

from database.db_connection import PostgresDB
from database.schemas import BaseORM

config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

Config()
username = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
db_name = os.getenv('POSTGRES_DB')
context.configure(
    compare_type=True,
    compare_server_default=True,
    include_schemas=True,
    dialect_name="sqlalchemy",
    url=f"postgresql://{username}:{password}@{host}:{port}/{db_name}"
)
config.set_main_option('sqlalchemy.url', f"postgresql://{username}:{password}@{host}:{port}/{db_name}")

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = BaseORM.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = PostgresDB().get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
            include_schemas=True
        )

        with context.begin_transaction():
            context.run_migrations()


if not context.is_offline_mode():
    run_migrations_online()
