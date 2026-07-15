import logging

from app.contexts.request import request_context


class RequestContextFilter(logging.Filter):
    """
    A logging filter that adds request context information to log records.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        log_context = request_context.get()
        if log_context:
            record.request_id = log_context.request_id
        return True
