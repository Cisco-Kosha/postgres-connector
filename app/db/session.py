import sqlalchemy.orm
from sqlalchemy import create_engine, inspect, MetaData, Column, Table, String, Integer
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper, clear_mappers
from app.core.config import *

from app.db.core import Database
import logging

logger = logging.getLogger("postgres-connector")
logger.setLevel(logging.INFO)

Base = declarative_base()


def get_sqlalchemy_engine():
    return create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)


def get_session_local(engine: Engine) -> sqlalchemy.orm.sessionmaker:
    return sessionmaker(autocommit=False, autoflush=True, bind=engine)


def get_inspector(engine: Engine) -> sqlalchemy.engine.reflection.Inspector:
    inspector = None
    try:
        inspector = inspect(engine).from_engine(engine)
    except sqlalchemy.exc.OperationalError as e:
        logger.error(e)
    return inspector


def get_sqlalchemy_db():
    db = Database(settings.SQLALCHEMY_DATABASE_URI)
    return db
