from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_injector import InjectorMiddleware
from injector import Injector

from app.middlewares.close_database_sessions import CloseDatabaseSessionsMiddleware
from app.middlewares.log_request import LogRequestMiddleware
from app.middlewares.request_cancelled import RequestCancelledMiddleware
from app.middlewares.request_context import RequestContextMiddleware


def setup_middlewares(app: FastAPI, injector: Injector) -> None:
    app.add_middleware(CloseDatabaseSessionsMiddleware)
    app.add_middleware(InjectorMiddleware, injector=injector)
    app.add_middleware(RequestCancelledMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(LogRequestMiddleware)
