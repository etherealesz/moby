from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from infrastructures.databases.utils.session_helper import close_all_db_sessions


class CloseDatabaseSessionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        try:
            response = await call_next(request)
        finally:
            await close_all_db_sessions(request.app.state.injector)

        return response
