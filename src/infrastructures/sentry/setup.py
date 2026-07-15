import sentry_sdk
import typer
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from core.config.settings import ENVIRONMENT, settings
from core.exceptions.base import ApplicationError
from core.exceptions.network import RequestCancelledError
from core.logger.factory import create_app_logger

logger = create_app_logger()

IGNORE_ERRORS = typer.Exit, ApplicationError, RequestCancelledError


def setup_sentry() -> None:
    """
    Initialize the Sentry SDK with the provided configuration settings.
    """

    try:
        sentry_sdk.init(
            dsn=settings.sentry.dsn,
            server_name=settings.application.name,
            release=settings.application.version,
            environment=ENVIRONMENT,
            traces_sample_rate=1.0,
            send_default_pii=True,
            integrations=[FastApiIntegration(), StarletteIntegration()],
            enable_logs=True,
            before_send=_before_send_errors,
        )
    except Exception as exc:
        logger.error(f"Failed to initialize Sentry: {exc}")


def _before_send_errors(event, hint):
    """
    Filter out specific exceptions from being sent to Sentry.

    Args:
        event (Event): The event data that is about to be sent to Sentry.
        hint (Hint): Additional information about the event, including exception details.

    Returns:
        Event | None: The event to be sent to Sentry, or None if the event
    """

    if "exc_info" not in hint:
        return event

    _, exc_value, _ = hint["exc_info"]
    if isinstance(exc_value, IGNORE_ERRORS):
        return None

    return event
