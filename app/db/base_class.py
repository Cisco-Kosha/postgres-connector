from typing import Any
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, inspect, MetaData, Table

from sqlalchemy.ext.declarative import as_declarative, declared_attr

from app.core.config import settings


@as_declarative()
class Base:

    id: Any
    __name__: str
    # Generate __tablename__ automatically

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
