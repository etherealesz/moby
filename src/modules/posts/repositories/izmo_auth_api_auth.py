import httpx
from injector import inject

from modules.posts.schemas.request import SIzmoAuthPostAuthLoginRequest


class IzmoAuthAPIAuthRepository:
    @inject
    def __init__(self, http_client: httpx.AsyncClient):
        self._client = http_client

    async def authenticate(self, username: str, password: str):
        data = SIzmoAuthPostAuthLoginRequest(
            username=username,
            password=password,
        )

        await self._client.post("/auth/login", json=data.model_dump())
