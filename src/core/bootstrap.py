import asyncio
import logging
import sys

from injector import Injector

from core.config.settings import settings
from core.logger.setup import setup_logger
from infrastructures.databases.database_manager import DatabaseManager
from infrastructures.persistence.model_loader.master import load_master_models
from infrastructures.task_launcher.base import TaskLauncher

_bootstrapped = False


def bootstrap_runtime() -> None:
    global _bootstrapped
    if _bootstrapped:
        return

    setup_logger(settings.logging.level)
    logger = logging.getLogger()

    load_master_models()

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        logger.info("Set event loop policy to WindowsSelectorEventLoopPolicy")

    _bootstrapped = True


async def bootstrap_startup(injector: Injector) -> None:
    pass


async def bootstrap_shutdown(injector: Injector) -> None:
    await injector.get(TaskLauncher).wait_for_tasks_until_completed()

    if injector.binder.has_binding_for(DatabaseManager):
        await injector.get(DatabaseManager).dispose()
