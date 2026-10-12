from typing import Iterable

from injector import Injector, Module

from container.database.master import (
    CDatabaseMasterModule,
    CSingletonDatabaseMasterModule,
)
from container.task_launcher import CTaskLauncherModule
from modules.classification.container import CClassificationModule
from modules.facilities.container import CFacilityModule
from modules.navigation.container import CNavigationModule
from modules.waste_categories.container import CWasteCategoryModule


def _create_app_modules() -> Iterable[Module]:
    return {
        CWasteCategoryModule(),
        CFacilityModule(),
        CNavigationModule(),
        CClassificationModule(),
    }


def create_injector() -> Injector:
    app_modules = _create_app_modules()

    return Injector(
        {
            CDatabaseMasterModule(),
            CTaskLauncherModule(),
            *app_modules,
        }
    )


def create_command_injector() -> Injector:
    app_modules = _create_app_modules()

    return Injector(
        {
            CSingletonDatabaseMasterModule(),
            CTaskLauncherModule(),
            *app_modules,
        }
    )
