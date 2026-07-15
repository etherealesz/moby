from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.factory import create_app
from infrastructures.databases.master.session import DatabaseMasterSession
from tests.core.container.factory import create_test_injector

injector = create_test_injector()
test_app = create_app(injector=injector)
test_client = TestClient(test_app)


@pytest.fixture
def mock_database_master_session() -> DatabaseMasterSession:
    return MagicMock(spec=DatabaseMasterSession)
