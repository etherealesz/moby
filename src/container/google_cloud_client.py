from injector import Binder, Module, singleton

from core.config.settings import ENVIRONMENT
from infrastructures.google_cloud.client import GoogleCloudStorageClient
from infrastructures.google_cloud.client_factory import create_google_cloud_storage_client


class CGoogleCloudClientModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(
            GoogleCloudStorageClient,
            to=create_google_cloud_storage_client(environment=ENVIRONMENT),
            scope=singleton,
        )
