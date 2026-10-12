from fastapi import FastAPI

from app.routes.factory import (
    create_api_router,
    create_root_router,
    create_webhook_router,
    create_websocket_router,
)


def setup_routes(app: FastAPI) -> None:
    root_router = create_root_router()
    api_router = create_api_router()
    websocket_router = create_websocket_router()
    webhook_router = create_webhook_router()

    app.include_router(root_router)
    app.include_router(api_router)
    app.include_router(websocket_router)
    app.include_router(webhook_router)
