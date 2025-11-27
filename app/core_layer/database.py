from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core_layer.config import settings
from app.repository_layer.models.models import Project, Task, DatabaseBaseModel  # noqa

engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI), future=True, echo=True
)


def get_async_session_maker():
    async_session_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    return async_session_factory


async def create_tables_and_indexes(self):
    # Tables can be created by using alembic or calling this function
    async with self.engine.begin() as conn:
        await conn.run_sync(DatabaseBaseModel.metadata.drop_all)
        await conn.run_sync(DatabaseBaseModel.metadata.create_all)
