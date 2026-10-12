from fastapi.testclient import TestClient

from app.factory import create_app
from container.factory import create_injector
from infrastructures.persistence.model_loader.master import load_master_models

load_master_models()

injector = create_injector()
test_app = create_app(injector=injector)
test_client = TestClient(test_app)
