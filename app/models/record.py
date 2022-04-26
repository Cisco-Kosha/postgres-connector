from typing import TYPE_CHECKING, Any

from sqlalchemy import create_engine, Table

from app.db.base_class import Base
from ..core.config import settings

from app.db.metadata import table_metadata

if TYPE_CHECKING:
    from .user import User  # noqa: F401

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

def get_table_object():
    class TableModel(Base):
        """
        Defines the table model
        """
        __tablename__ = table_metadata.get_table()
        if __tablename__ is not None:
            __table__ = Table(__tablename__, Base.metadata,
                              autoload_with=engine)

            columns = __table__.columns
            primary_key = __table__.primary_key

        def __init__(self, **kwargs):
            for arg in kwargs.copy():
                val = kwargs.pop(arg)
                setattr(self, arg, val)

        def __repr__(self) -> str:
            return f"<{self.__tablename__} {self.primary_key}>"

        @property
        def serialize(self) -> Any:
            """
            Return record in serializeable format
            """
            mydict = {}
            for key in self.columns.keys():
                mydict[key] = getattr(self, key)
            return mydict

    return TableModel
