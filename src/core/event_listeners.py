from sqlalchemy import event, Engine


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
