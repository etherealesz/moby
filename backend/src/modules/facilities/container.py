from injector import Binder, Module

from modules.facilities.repositories.facility.protocol import FacilityRepository
from modules.facilities.repositories.facility.repository import IFacilityRepository
from modules.facilities.use_cases.get_facilities.use_case import GetFacilitiesUseCase


class CFacilityModule(Module):
    def configure(self, binder: Binder) -> None:
        self._register_repositories(binder)
        self._register_use_cases(binder)

    def _register_repositories(self, binder: Binder) -> None:
        binder.bind(FacilityRepository, to=IFacilityRepository)

    def _register_use_cases(self, binder: Binder) -> None:
        binder.bind(GetFacilitiesUseCase, to=GetFacilitiesUseCase)
