from fastapi import status

from core.constants.url import BASE_API_URL_PREFIX
from tests.conftest import test_client


def test_about_api():
    response = test_client.get(f"{BASE_API_URL_PREFIX}/info/about")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["title"] == "Tentang MOBY"


def test_help_api():
    response = test_client.get(f"{BASE_API_URL_PREFIX}/info/help")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["data"]["sections"]) == 4


def test_route_validation_error():
    response = test_client.post(
        f"{BASE_API_URL_PREFIX}/route",
        json={"latitude": -6.2, "longitude": 106.8, "category": "Kaca"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
