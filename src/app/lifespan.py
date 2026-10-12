from contextlib import asynccontextmanager

from fastapi import FastAPI
from injector import Injector

from core.bootstrap import bootstrap_shutdown, bootstrap_startup


@asynccontextmanager
async def lifespan(_: FastAPI, injector: Injector):
    await bootstrap_startup(injector)

    yield

    await bootstrap_shutdown(injector)
