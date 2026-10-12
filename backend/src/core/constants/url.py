from core.config.settings import settings

BASE_URL_PREFIX = f"/{settings.application.name.lower().replace(' ', '-')}"
BASE_API_URL_PREFIX = f"{BASE_URL_PREFIX}/api"
BASE_WEBSOCKET_URL_PREFIX = f"{BASE_URL_PREFIX}/ws"
BASE_WEBHOOK_URL_PREFIX = f"{BASE_URL_PREFIX}/webhook"

LOCAL_DOCS_URL = "/docs"
LOCAL_REDOC_URL = "/redoc"
LOCAL_OPENAPI_URL = "/openapi.json"

NON_LOCAL_DOCS_URL = f"{BASE_URL_PREFIX}/docs"
NON_LOCAL_REDOC_URL = f"{BASE_URL_PREFIX}/redoc"
NON_LOCAL_OPENAPI_URL = f"{BASE_URL_PREFIX}/openapi.json"
