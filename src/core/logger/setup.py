import logging

from uvicorn.logging import DefaultFormatter

from core.config.loader import get_runtime_environment
from core.constants.environment import DEVELOPMENT_RUNTIME_ENVIRONMENTS
from core.constants.logger import UVICORN_AND_FASTAPI_LOGGERS
from core.types.logging import LoggingLevel


def setup_logger(level_name: LoggingLevel = "info"):
    """
    Setup the root logger with a console handler and a custom formatter.

    Args:
        level_name (LoggingLevel): The logging level as a string. Defaults to "debug".

    Returns:
        None
    """

    level = getattr(logging, level_name.upper(), logging.INFO)

    _setup_external_loggers()

    formatter = _create_formatter()
    console_handler = _create_console_handler(level, formatter)

    _setup_root_logger(console_handler)


def _setup_external_loggers() -> None:
    """
    Configure external loggers (e.g., uvicorn and fastapi) to prevent them
    from propagating logs to the root logger, which can lead to duplicate log entries.

    Returns:
        None
    """

    runtime_environment = get_runtime_environment()
    in_development_runtime_environment = (
        runtime_environment in DEVELOPMENT_RUNTIME_ENVIRONMENTS
        or runtime_environment == ""
    )
    watchfiles_logger = logging.getLogger("watchfiles")
    httpx_logger = logging.getLogger("httpx")
    httpcore_logger = logging.getLogger("httpcore")
    asyncio_logger = logging.getLogger("asyncio")
    opentelemetry_logger = logging.getLogger("opentelemetry")
    google_logger = logging.getLogger("google")

    # Remove third-party libraries logs to prevent cluttering the console,
    # as they are not relevant for the application logs.
    watchfiles_logger.setLevel(logging.WARNING)
    httpx_logger.setLevel(logging.WARNING)
    httpcore_logger.setLevel(logging.WARNING)
    asyncio_logger.setLevel(logging.WARNING)
    opentelemetry_logger.setLevel(logging.WARNING)
    google_logger.setLevel(logging.WARNING)

    for name in UVICORN_AND_FASTAPI_LOGGERS:
        logger = logging.getLogger(name)
        logger.propagate = False
        if in_development_runtime_environment:
            logger.handlers.clear()
        else:
            logger.handlers = [logging.NullHandler()]


def _create_formatter() -> logging.Formatter:
    """
    Create a custom formatter for log messages.

    Returns:
        logging.Formatter: A configured formatter for log messages.
    """

    format = "%(levelprefix)s [%(asctime)s] %(message)s"
    return DefaultFormatter(fmt=format, datefmt="%Y-%m-%d %H:%M:%S")


def _create_console_handler(
    level: int,
    formatter: logging.Formatter,
) -> logging.StreamHandler:
    """
    Create a console handler with the specified logging level.

    Args:
        level (int): The logging level for the console handler.
        formatter (logging.Formatter): The formatter to use for the console handler.

    Returns:
        logging.StreamHandler: A configured console handler.
    """

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    return console_handler


def _setup_root_logger(console_handler: logging.StreamHandler) -> None:
    """
    Setup the root logger with the provided console handler.

    Args:
        console_handler (logging.StreamHandler): The console handler to add to the root logger.

    Returns:
        None
    """

    root_logger = logging.getLogger()
    root_logger.setLevel(console_handler.level)
    root_logger.handlers = [console_handler]
