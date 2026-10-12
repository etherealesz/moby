import uuid
from datetime import datetime

from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

from app.contexts.request import RequestContext, request_context


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex.replace(
            "-", ""
        )
        timestamp = request.headers.get("X-Timestamp")
        if timestamp:
            timestamp = datetime.fromisoformat(timestamp)
        else:
            timestamp = datetime.now()

        context = RequestContext(
            request_id=request_id,
            timestamp=timestamp,
            ip=request.client.host if request.client else None,
            path=request.url.path,
            method=request.method,
        )
        token = request_context.set(context)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Timestamp"] = timestamp.isoformat()
        request_context.reset(token)

        return response
