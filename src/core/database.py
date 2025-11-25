import logging
from contextlib import AbstractContextManager, asynccontextmanager
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from src.models.DatabaseMixins import DatabaseBaseModel
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger("")


# TODO consider switch to postgres - the full text search in particular seems handy
class Database:

    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(db_url, future=True)
        self.async_session_factory = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=True
        )

    @asynccontextmanager
    async def session(self) -> Callable[..., AbstractContextManager[AsyncSession]]:
        session: AsyncSession = self.async_session_factory()
        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            await session.close()

    async def shutdown(self):
        self._engine.dispose()
