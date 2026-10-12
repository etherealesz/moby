from fastapi_injector import request_scope
from injector import Module, provider, singleton

from infrastructures.databases.database_manager import DatabaseManager
from infrastructures.databases.master import (
    DatabaseMasterEngine,
    DatabaseMasterSession,
    DatabaseMasterSessionMaker,
    database_master_dsn,
)


class CDatabaseMasterModule(Module):
    @provider
    @singleton
    def provide_database_manager(self) -> DatabaseManager:
        return DatabaseManager(database_master_dsn, pool_size=10, max_overflow=10)

    @provider
    @singleton
    def provide_engine(self, manager: DatabaseManager) -> DatabaseMasterEngine:
        return manager.engine

    @provider
    @singleton
    def provide_session_maker(
        self,
        manager: DatabaseManager,
    ) -> DatabaseMasterSessionMaker:
        return manager.session_maker

    @provider
    @request_scope
    def provide_session(self, manager: DatabaseManager) -> DatabaseMasterSession:
        return manager.create_session()


class CSingletonDatabaseMasterModule(Module):
    @provider
    @singleton
    def provide_database_manager(self) -> DatabaseManager:
        return DatabaseManager(database_master_dsn, pool_size=1, max_overflow=0)

    @provider
    @singleton
    def provide_engine(self, manager: DatabaseManager) -> DatabaseMasterEngine:
        return manager.engine

    @provider
    @singleton
    def provide_session_maker(
        self,
        manager: DatabaseManager,
    ) -> DatabaseMasterSessionMaker:
        return manager.session_maker

    @provider
    @singleton
    def provide_session(self, manager: DatabaseManager) -> DatabaseMasterSession:
        return manager.create_session()
