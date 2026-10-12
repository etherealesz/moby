from injector import Binder, Module

from modules.navigation.repositories.road_graph.protocol import RoadGraphRepository
from modules.navigation.repositories.road_graph.repository import IRoadGraphRepository
from modules.navigation.services.navigation_service.service import NavigationService
from modules.navigation.services.road_graph_manager.service import RoadGraphManager
from modules.navigation.use_cases.find_route.use_case import FindRouteUseCase


class CNavigationModule(Module):
    def configure(self, binder: Binder) -> None:
        self._register_repositories(binder)
        self._register_services(binder)
        self._register_use_cases(binder)

    def _register_repositories(self, binder: Binder) -> None:
        binder.bind(RoadGraphRepository, to=IRoadGraphRepository)

    def _register_services(self, binder: Binder) -> None:
        binder.bind(RoadGraphManager, to=RoadGraphManager)
        binder.bind(NavigationService, to=NavigationService)

    def _register_use_cases(self, binder: Binder) -> None:
        binder.bind(FindRouteUseCase, to=FindRouteUseCase)
