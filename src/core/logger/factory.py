import logging

from uvicorn.logging import DefaultFormatter

from core.logger.filter import RequestContextFilter
from core.logger.formatter import FormatterWithExtra


def create_app_logger():
    logger = logging.getLogger("app")
    if logger.handlers:
        return logger

    format = "%(levelprefix)s [%(asctime)s] [%(module)s:%(funcName)s] %(message)s"
    formatter = FormatterWithExtra(fmt=format, datefmt="%Y-%m-%d %H:%M:%S")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.addFilter(RequestContextFilter())

    logger.propagate = False
    logger.addHandler(handler)

    return logger


def create_request_logger() -> logging.Logger:
    logger = logging.getLogger("app.request")
    if logger.handlers:
        return logger

    format = "%(levelprefix)s [%(asctime)s] %(message)s"
    formatter = DefaultFormatter(fmt=format, datefmt="%Y-%m-%d %H:%M:%S")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    return logger
