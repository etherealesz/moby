from injector import Binder, Module, singleton
from modules.navigation.use_cases.find_route import FindRouteUseCase

class CNavigationModule(Module):
    def configure(self, binder: Binder) -> None:
        self._register_usecases(binder)
        
    def _register_usecases(self, binder: Binder) -> None:
        binder.bind(FindRouteUseCase, to=FindRouteUseCase)
