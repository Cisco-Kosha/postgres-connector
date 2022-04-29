from sqlalchemy import create_engine, inspect, MetaData, Column, Table, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper, clear_mappers
from app.core.config import settings

from app.db.core import Database


Base = declarative_base()


engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

Inspector = inspect(engine)
db = Database(settings.SQLALCHEMY_DATABASE_URI)
inspector = Inspector.from_engine(engine)
print(db.get_schema_names(inspector=inspector))
