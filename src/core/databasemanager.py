import logging
from contextlib import AbstractContextManager, asynccontextmanager
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.models.database_mixins import DatabaseBaseModel

logger = logging.getLogger("")


class DatabaseManager:

    # noinspection PyTypeChecker
    def __init__(self, db_url: str) -> None:
        self.engine = create_async_engine(db_url, future=True, echo=True)
        self.async_session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=True
        )

    async def create_tables_and_indexes(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(DatabaseBaseModel.metadata.drop_all)
            await conn.run_sync(DatabaseBaseModel.metadata.create_all)

    def get_async_session(self) -> AsyncSession:
        return self.async_session_factory()

    async def shutdown(self):
        await self.engine.dispose()
