import logging
from contextlib import contextmanager

import re
import os

from sqlalchemy import event, exc
from sqlalchemy.engine import Engine, create_engine
from sqlite3 import Connection as SQLite3Connection
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import Pool

_logger = logging.getLogger(__name__)

POOL_RECYCLE = 100
POOL_SIZE = 1  # 1 for monothreaded, otherwise should be number of threads


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor =dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_key=OM;")
        cursor.close()


@event.listens_for(Engine, "connect")
def connect(dbapi_connection, connection_record):
    """
    Store the process pid in the connection record
    """
    connection_record.info['pid'] = os.getpid()


@event.listens_for(Pool, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxi):
    """
    Make sure we do not re-use connection with different process (this is for oracle)
    """
    pid = os.getpid()
    if connection_record.info['pid'] != pid:
        connection_record.connection = connection_proxi.connection = None
        raise exc.DisconnectionError(
            "Connection belongs to pid: {} - attempting to check out in pid: {}".format(connection_record.info['pid'],
                                                                                        pid))


def blank_password(database_url):
    """
    remove password info from database url
    :param database_url:
    :return:
    """
    return re.sub(':[^@:]*@', ':xxx@', database_url)


@contextmanager
def session_scope(session_builder):
    """
    Provides a transactional scope around a series of operations
    :param session_builder:
    :return:
    """
    session = session_builder()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class SQLAlchemyQueries:
    def __init__(self, database_url, declarative_base=None, expire_on_commit=True):
        _logger.info('Using <{}>'.format(blank_password(database_url)))
        if 'sqlite' in database_url:
            # no pool recycling for in-memory sqlite, disable it
            self._engine = create_engine(database_url, pool_recycle=-1)
        else:
            kwargs = {'pool_recycle': POOL_RECYCLE, 'pool_size': POOL_SIZE}
            self.engine = create_engine(database_url, **kwargs)
        self._session_maker = sessionmaker(bind=self._engine, expire_on_commit=expire_on_commit)
        if declarative_base:
            declarative_base.metadata.create_all(bind=self._engine, checkfirst=True)

    def session_scope(self):
        return session_scope(self._session_maker)