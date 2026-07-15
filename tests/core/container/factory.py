from injector import Injector

from core.container.database import DatabaseModule
from core.container.http_client import HTTPClientModule
from src.core.container.repository import RepositoryModule
from src.core.container.use_case import UseCaseModule


def create_test_injector() -> Injector:
    return Injector(
        [
            UseCaseModule(),
            RepositoryModule(),
            DatabaseModule(),
            HTTPClientModule(),
        ]
    )
