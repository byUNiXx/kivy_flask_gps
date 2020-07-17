import os
from sqlalchemy import event
from sqlalchemy.engine import Engine
from _sqlite3 import Connection as SQLite3Connection

basedir = os.path.abspath(os.path.dirname(__file__))

TESTING = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
WTF_CSRF_ENABLED = False


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
