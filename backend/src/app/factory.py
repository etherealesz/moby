import logging

from fastapi import FastAPI, status
from fastapi_injector import attach_injector
from injector import Injector

from app.exceptions.setup import setup_exception_handlers
from app.lifespan import lifespan
from app.middlewares.setup import setup_middlewares
from app.routes.setup import setup_routes
from app.schemas.predefined import SStandardInternalServerErrorResponse
from app.utils.url import get_docs_url
from core.config.settings import settings

logger = logging.getLogger()


def create_app(injector: Injector) -> FastAPI:
    docs_url, redoc_url, openapi_url = get_docs_url()
    app = FastAPI(
        title=settings.application.name,
        debug=settings.application.debug,
        lifespan=lambda app: lifespan(app, injector),
        redirect_slashes=False,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        version=settings.application.version,
        responses={
            status.HTTP_500_INTERNAL_SERVER_ERROR: {
                "model": SStandardInternalServerErrorResponse
            },
        },
    )

    setup_middlewares(app, injector=injector)
    setup_routes(app)
    setup_exception_handlers(app)

    attach_injector(app, injector)

    return app
