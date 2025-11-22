from sqlalchemy import event
import logging
from contextlib import AbstractContextManager, asynccontextmanager
from typing import Callable

from sqlalchemy import create_engine, orm
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from src.models.db_models import DatabaseBaseModel

logger = logging.getLogger("")


class Database:

    def __init__(self, db_url: str, connection_args: dict) -> None:
        self._engine = create_engine(db_url, connect_args=connection_args)
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def create_database(self) -> None:
        DatabaseBaseModel.metadata.create_all(self._engine)

    @event.listens_for(Engine, "connect")
    def enable_foreign_key_constraint_sqlite(dbapi_connection, connection_record):
        # the sqlite3 driver will not set PRAGMA foreign_keys
        # if autocommit=False; set to True temporarily
        ac = dbapi_connection.autocommit
        dbapi_connection.autocommit = True
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
        print("SQlite foreign keys constraints enabled")
        # restore previous autocommit setting
        dbapi_connection.autocommit = ac

    @asynccontextmanager
    async def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()

    async def shutdown(self):
        self._engine.dispose()
