import logging

from injector import Injector

from core.config.settings import settings
from core.logger.setup import setup_logger
from infrastructures.databases.master import DatabaseMasterEngine
from infrastructures.task_launcher.base import TaskLauncher

_bootstrapped = False


def bootstrap_runtime() -> None:
    """
    Bootstraps the runtime environment for the application.
    """

    global _bootstrapped
    if _bootstrapped:
        return

    setup_logger(settings.logging.level)
    logger = logging.getLogger()

    import sys

    if sys.platform == "win32":
        import asyncio

        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        logger.info("Set event loop policy to WindowsSelectorEventLoopPolicy")

    _bootstrapped = True


async def bootstrap_shutdown(injector: Injector) -> None:
    """
    Bootstraps the shutdown process for the application, ensuring that all resources are properly released.

    Args:
        injector (Injector): The dependency injection container used to manage application dependencies.
    """

    await injector.get(TaskLauncher).wait_for_tasks_until_completed()

    if injector.binder.has_binding_for(DatabaseMasterEngine):
        await injector.get(DatabaseMasterEngine).dispose()
