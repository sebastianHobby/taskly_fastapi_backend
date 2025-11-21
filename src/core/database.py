from sqlalchemy import create_engine, Engine
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
import src.models
from src.models.db_models import DatabaseBaseModel

from contextlib import contextmanager, AbstractContextManager, asynccontextmanager
from typing import Callable
import logging

from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


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
