from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLITE_DATABASE_URL = f"sqlite:///tasklyData.db"
# connect_args = {"check_same_thread": False}
# engine = create_engine(SQLITE_DATABASE_URL, connect_args=connect_args)
SQLITE_DATABASE_URL = "sqlite+aiosqlite:///tasklyAsync.db"
engine = create_async_engine(SQLITE_DATABASE_URL, future=True)

Base = declarative_base()
# SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionFactory = async_sessionmaker(bind=engine)


# By default SQLite does not enforce foreign key constraints.
# This function enables constraint.
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # the sqlite3 driver will not set PRAGMA foreign_keys
    # if autocommit=False; set to True temporarily
    ac = dbapi_connection.autocommit
    dbapi_connection.autocommit = True
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    print("Running set-sqlite-pragma to turn on foreign keys constraints")
    # restore previous autocommit setting
    dbapi_connection.autocommit = ac


async def create_database_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


# asyncio.run(init_models())
#
# def create_database_and_tables():
#     print("Creating database and tables")
#     Base.metadata.create_all(bind=engine)


def get_database_session():
    db_session = SessionFactory()
    try:
        yield db_session
    finally:
        db_session.close()
