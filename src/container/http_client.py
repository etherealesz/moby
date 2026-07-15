from injector import Binder, Module, singleton

from core.config.settings import settings
from infrastructures.http.client_factory import create_http_client
from infrastructures.http.izmo_auth.client import IzmoAuthAPIHTTPClient


class CHTTPClientModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(
            IzmoAuthAPIHTTPClient,
            to=create_http_client(
                class_=IzmoAuthAPIHTTPClient,
                base_url=settings.external_service.izmo_auth.base_url,
            ),
            scope=singleton,
        )
