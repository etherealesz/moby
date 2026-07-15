from typing import cast

from fastapi_injector import request_scope
from injector import Module, provider, singleton
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from infrastructures.databases.master import (
    DatabaseMasterEngine,
    DatabaseMasterSession,
    DatabaseMasterSessionMaker,
    database_master_dsn,
)


class CDatabaseMasterModule(Module):
    @provider
    @singleton
    def provide_engine(self) -> DatabaseMasterEngine:
        engine = create_async_engine(
            database_master_dsn,
            pool_size=10,
            max_overflow=10,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 10},
        )
        return cast(DatabaseMasterEngine, engine)

    @provider
    @singleton
    def provide_session_maker(
        self,
        engine: DatabaseMasterEngine,
    ) -> DatabaseMasterSessionMaker:
        session_maker = async_sessionmaker(
            bind=engine,
            class_=DatabaseMasterSession,
            expire_on_commit=False,
        )
        return cast(DatabaseMasterSessionMaker, session_maker)

    @provider
    @request_scope
    def provide_session(
        self,
        session_maker: DatabaseMasterSessionMaker,
    ) -> DatabaseMasterSession:
        return session_maker()


class CSingletonDatabaseMasterModule(Module):
    @provider
    @singleton
    def provide_engine(self) -> DatabaseMasterEngine:
        engine = create_async_engine(
            database_master_dsn,
            pool_size=1,
            max_overflow=0,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 10},
        )
        return cast(DatabaseMasterEngine, engine)

    @provider
    @singleton
    def provide_session_maker(
        self,
        engine: DatabaseMasterEngine,
    ) -> DatabaseMasterSessionMaker:
        session_maker = async_sessionmaker(
            bind=engine,
            class_=DatabaseMasterSession,
            expire_on_commit=False,
        )
        return cast(DatabaseMasterSessionMaker, session_maker)

    @provider
    @singleton
    def provide_session(
        self,
        session_maker: DatabaseMasterSessionMaker,
    ) -> DatabaseMasterSession:
        return session_maker()
