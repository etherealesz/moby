from fastapi import status

from core.constants.url import BASE_URL_PREFIX
from tests.conftest import test_client


def test_health_api():
    response = test_client.get(f"{BASE_URL_PREFIX}/health")
    assert response.status_code == status.HTTP_200_OK
