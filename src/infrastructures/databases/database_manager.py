from typing import cast

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from infrastructures.databases.master import (
    DatabaseMasterEngine,
    DatabaseMasterSession,
    DatabaseMasterSessionMaker,
)


class DatabaseManager:
    def __init__(self, dsn: str, pool_size: int, max_overflow: int) -> None:
        engine = create_async_engine(
            dsn,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 10},
        )
        self._engine = cast(DatabaseMasterEngine, engine)
        self._session_maker = cast(
            DatabaseMasterSessionMaker,
            async_sessionmaker(
                bind=engine,
                class_=DatabaseMasterSession,
                expire_on_commit=False,
            ),
        )

    @property
    def engine(self) -> DatabaseMasterEngine:
        return self._engine

    @property
    def session_maker(self) -> DatabaseMasterSessionMaker:
        return self._session_maker

    def create_session(self) -> DatabaseMasterSession:
        return self._session_maker()

    async def dispose(self) -> None:
        await self._engine.dispose()
