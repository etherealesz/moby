import time

from fastapi import Request, Response
from starlette import status
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

from core.exceptions.network import RequestCancelledError
from core.logger.factory import create_request_logger

logger = create_request_logger()


class LogRequestMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log HTTP requests and responses.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        start_time = time.perf_counter()
        response: Response | None = None

        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            if isinstance(exc, RequestCancelledError):
                # Keep returning response with status code 499 to indicate client
                # closed the connection, this is needed for logging purposes, so
                # we can track requests that cancelled by clients.
                response = Response(status_code=499)
                return response

            raise exc
        finally:
            process_time = time.perf_counter() - start_time
            client_host = request.client.host if request.client else '"-"'
            http_version = request.scope.get("http_version", "1.1")
            user_agent = request.headers.get("user-agent", "-")
            request_content_length = request.headers.get("content-length", '"-"')
            request_method = request.method
            request_url_path = request.url.path
            response_content_length = (
                response.headers.get("content-length", '"-"') if response else '"-"'
            )

            # Safely get the response status code, defaulting to 500 if
            # response is None, which indicates an unexpected error raised.
            response_status_code = (
                response.status_code
                if response
                else status.HTTP_500_INTERNAL_SERVER_ERROR
            )

            response_log = '[{:.2f}ms] {} - "{} {} HTTP/{}" {} {} {} "{}"'.format(
                process_time * 1000,
                client_host,
                request_method,
                request_url_path,
                http_version,
                response_status_code,
                request_content_length,
                response_content_length,
                user_agent,
            )
            logger.info(response_log)
