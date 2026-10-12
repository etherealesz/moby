from typing import TypeVar

from injector import Injector
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger.factory import create_app_logger
from infrastructures.databases.master import DatabaseMasterSession

logger = create_app_logger()

T = TypeVar("T", bound=AsyncSession)


async def close_all_db_sessions(injector: Injector) -> None:
    await close_db_session(
        injector=injector,
        class_=DatabaseMasterSession,
        database_name="master",
    )


async def close_db_session(
    injector: Injector,
    class_: type[T],
    database_name: str,
) -> None:
    try:
        if injector.binder.has_binding_for(class_):
            db_session: T = injector.get(class_)
            await db_session.close()
    except Exception:
        logger.critical(
            f"An error occurred while closing database {database_name} session",
            exc_info=True,
        )
