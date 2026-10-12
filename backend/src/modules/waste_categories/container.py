from injector import Binder, Module

from modules.waste_categories.repositories.waste_category.protocol import (
    WasteCategoryRepository,
)
from modules.waste_categories.repositories.waste_category.repository import (
    IWasteCategoryRepository,
)
from modules.waste_categories.use_cases.get_categories.use_case import (
    GetCategoriesUseCase,
)


class CWasteCategoryModule(Module):
    def configure(self, binder: Binder) -> None:
        self._register_repositories(binder)
        self._register_use_cases(binder)

    def _register_repositories(self, binder: Binder) -> None:
        binder.bind(WasteCategoryRepository, to=IWasteCategoryRepository)

    def _register_use_cases(self, binder: Binder) -> None:
        binder.bind(GetCategoriesUseCase, to=GetCategoriesUseCase)
