from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from core.config.settings import settings
from infrastructures.databases.utils.dsn import build_dsn

ssl_mode = "require"
if settings.database.master.host in ["localhost", "127.0.0.1"]:
    ssl_mode = None

database_master_dsn = build_dsn(
    provider="postgresql",
    driver="psycopg",
    host=settings.database.master.host,
    port=settings.database.master.port,
    user=settings.database.master.user,
    password=settings.database.master.password,
    db_name=settings.database.master.name,
    ssl_mode=ssl_mode,
)


class DatabaseMasterEngine(AsyncEngine):
    pass


class DatabaseMasterSession(AsyncSession):
    pass


class DatabaseMasterSessionMaker(async_sessionmaker[DatabaseMasterSession]):
    pass
