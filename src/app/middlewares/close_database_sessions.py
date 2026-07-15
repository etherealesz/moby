from typing import TypeVar
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from core.logger.factory import create_app_logger
from infrastructures.databases.master import DatabaseMasterSession

logger = create_app_logger()


class CloseDatabaseSessionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        response = await call_next(request)

        await _close_db_sessions(
            class_=DatabaseMasterSession,
            request=request,
            database_name="master",
        )

        return response


T = TypeVar("T", bound=AsyncSession)


async def _close_db_sessions(
    class_: type[T],
    request: Request,
    database_name: str,
) -> None:
    """
    Closes database sessions gracefully.

    Args:
        class_ (type[T]): The database session class to close.
        request (Request): The incoming HTTP request.
        database_name (str): The name of the database for logging purposes.
    """

    try:
        db_session: T = request.app.state.injector.get(class_)
        await db_session.close()
    except Exception as exc:
        logger.critical(
            f"An error occured while closing database {database_name} session",
            exc_info=exc,
        )
