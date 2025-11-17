from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
import src.models
from src.models.DatabaseBaseModel import DatabaseBaseModel

engine = create_engine(
    "sqlite:///tasklyData.db", connect_args={"check_same_thread": False}
)


def create_database() -> None:
    """Sets up database engine to connect to database. Then creates tables based on SQLAlchemy Models imported from
    src.models. Note all models need to be imported prior to this method being run"""
    DatabaseBaseModel.metadata.create_all(bind=engine)


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


SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# SessionFactory = async_sessionmaker(bind=engine)


def get_database_session():
    db_session = SessionFactory()
    try:
        yield db_session
    finally:
        db_session.close()
