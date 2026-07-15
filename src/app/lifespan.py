from contextlib import asynccontextmanager

from fastapi import FastAPI
from injector import Injector

from core.bootstrap import bootstrap_shutdown
from core.managers.map_manager import MapManager


@asynccontextmanager
async def lifespan(_: FastAPI, injector: Injector):
    # Dapatkan singleton MapManager dan muat semua peta ke RAM saat startup
    map_manager = injector.get(MapManager)
    await map_manager.load_all_graphs_from_db()
    map_manager.load_all_graphs()

    yield

    await bootstrap_shutdown(injector)

