import importlib
import importlib.util
import pkgutil
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import modules
from core.config.settings import settings
from infrastructures.persistence.model.meta import BaseMetaData

for loader, module_name, is_package in pkgutil.iter_modules(modules.__path__):
    if importlib.util.find_spec(f"modules.{module_name}.model"):
        importlib.import_module(f"modules.{module_name}.model")
        continue

    if not importlib.util.find_spec(f"modules.{module_name}.models"):
        continue

    for loader, sub_module_name, is_package in pkgutil.iter_modules(
        importlib.import_module(f"modules.{module_name}.models").__path__
    ):
        importlib.import_module(f"modules.{module_name}.models.{sub_module_name}")

config = context.config

section = config.config_ini_section
config.set_section_option(section, "db_user", settings.database.master.user)
config.set_section_option(
    section,
    "db_password",
    settings.database.master.password,
)
config.set_section_option(section, "db_host", settings.database.master.host)
config.set_section_option(
    section,
    "db_port",
    str(settings.database.master.port),
)
config.set_section_option(
    section,
    "db_name",
    settings.database.master.name,
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = BaseMetaData


def include_object(object, name, type_, reflected, compare_to):
    return not (type_ == "table" and reflected and compare_to is None)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
