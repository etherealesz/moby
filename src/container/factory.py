from typing import Iterable

from injector import Injector, Module

from container.database.master import (
    CDatabaseMasterModule,
    CSingletonDatabaseMasterModule,
)
from container.google_cloud_client import CGoogleCloudClientModule
from container.http_client import CHTTPClientModule
from container.task_launcher import CTaskLauncherModule
from modules.posts.container import CPostModule
from modules.navigation.container import CNavigationModule
from core.managers.map_manager import CMapManagerModule


def _create_app_modules() -> Iterable[Module]:
    """
    Create and return a list of application modules to be used in the
    dependency injection container.

    Returns:
        Iterable[Module]: A set of application modules.
    """

    return {
        CPostModule(),
        CNavigationModule(),
    }


def create_injector() -> Injector:
    """
    Create and return an instance of the Injector with all registered application
    modules and core modules.

    Returns:
        Injector: An instance of the Injector with registered modules.
    """

    app_modules = _create_app_modules()

    return Injector(
        {
            CDatabaseMasterModule(),
            CGoogleCloudClientModule(),
            CHTTPClientModule(),
            CTaskLauncherModule(),
            CMapManagerModule(),
            *app_modules,
        }
    )


def create_command_injector() -> Injector:
    """
    Create and return an instance of the Injector with all registered application
    modules and core modules for command execution.

    Returns:
        Injector: An instance of the Injector with registered modules for command execution.
    """

    app_modules = _create_app_modules()

    return Injector(
        {
            CSingletonDatabaseMasterModule(),
            CGoogleCloudClientModule(),
            CHTTPClientModule(),
            CTaskLauncherModule(),
            CMapManagerModule(),
            *app_modules,
        }
    )
