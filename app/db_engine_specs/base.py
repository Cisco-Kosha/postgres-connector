import json
import logging
import re
from contextlib import closing
from datetime import datetime
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Match,
    NamedTuple,
    Optional,
    Pattern,
    Set,
    Tuple,
    Type,
    TYPE_CHECKING,
    Union,
)

from sqlalchemy import column, select, types
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.interfaces import Compiled, Dialect
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.engine.url import make_url, URL
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session
from sqlalchemy.sql import quoted_name, text
from sqlalchemy.sql.expression import ColumnClause, Select, TextAsFrom
from sqlalchemy.types import String, TypeEngine, UnicodeText
from typing_extensions import TypedDict

from app.utils.core import *

if TYPE_CHECKING:
    from app.db.core import Database


class BaseEngineSpec:
    engine = "base"  # str as defined in sqlalchemy.engine.engine
    engine_aliases: Set[str] = set()
    engine_name: Optional[
        str
    ] = None  # used for user messages, overridden in child classes
    column_type_mappings: Tuple[
        Tuple[
            Pattern[str],
            Union[TypeEngine, Callable[[Match[str]], TypeEngine]],
            GenericDataType,
        ],
        ...,
    ] = (
        (
            re.compile(r"^smallint", re.IGNORECASE),
            types.SmallInteger(),
            GenericDataType.NUMERIC,
        ),
        (
            re.compile(r"^int.*", re.IGNORECASE),
            types.Integer(),
            GenericDataType.NUMERIC,
        ),
        (
            re.compile(r"^bigint", re.IGNORECASE),
            types.BigInteger(),
            GenericDataType.NUMERIC,
        ),
        (
            re.compile(r"^decimal", re.IGNORECASE),
            types.Numeric(),
            GenericDataType.NUMERIC,
        ),
        (
            re.compile(r"^numeric", re.IGNORECASE),
            types.Numeric(),
            GenericDataType.NUMERIC,
        ),
        (re.compile(r"^float", re.IGNORECASE), types.Float(), GenericDataType.NUMERIC,),
        (
            re.compile(r"^double", re.IGNORECASE),
            types.Float(),
            GenericDataType.NUMERIC,
        ),
        (re.compile(r"^real", re.IGNORECASE), types.REAL, GenericDataType.NUMERIC,),
        (
            re.compile(r"^smallserial", re.IGNORECASE),
            types.SmallInteger(),
            GenericDataType.NUMERIC,
        ),
        (
            re.compile(r"^serial", re.IGNORECASE),
            types.Integer(),
            GenericDataType.NUMERIC,
        ),
        (
            re.compile(r"^bigserial", re.IGNORECASE),
            types.BigInteger(),
            GenericDataType.NUMERIC,
        ),
        (
            re.compile(r"^money", re.IGNORECASE),
            types.Numeric(),
            GenericDataType.NUMERIC,
        ),
        (
            re.compile(r"^string", re.IGNORECASE),
            types.String(),
            GenericDataType.STRING,
        ),
        (
            re.compile(r"^N((VAR)?CHAR|TEXT)", re.IGNORECASE),
            UnicodeText(),
            GenericDataType.STRING,
        ),
        (
            re.compile(r"^((VAR)?CHAR|TEXT|STRING)", re.IGNORECASE),
            String(),
            GenericDataType.STRING,
        ),
        (
            re.compile(r"^((TINY|MEDIUM|LONG)?TEXT)", re.IGNORECASE),
            String(),
            GenericDataType.STRING,
        ),
        (re.compile(r"^LONG", re.IGNORECASE), types.Float(), GenericDataType.NUMERIC,),
        (
            re.compile(r"^datetime", re.IGNORECASE),
            types.DateTime(),
            GenericDataType.TEMPORAL,
        ),
        (re.compile(r"^date", re.IGNORECASE), types.Date(), GenericDataType.TEMPORAL,),
        (
            re.compile(r"^timestamp", re.IGNORECASE),
            types.TIMESTAMP(),
            GenericDataType.TEMPORAL,
        ),
        (
            re.compile(r"^interval", re.IGNORECASE),
            types.Interval(),
            GenericDataType.TEMPORAL,
        ),
        (re.compile(r"^time", re.IGNORECASE), types.Time(), GenericDataType.TEMPORAL,),
        (
            re.compile(r"^bool.*", re.IGNORECASE),
            types.Boolean(),
            GenericDataType.BOOLEAN,
        ),
    )
    try_remove_schema_from_table_name = True

    @classmethod
    def get_engine(
            cls,
            database: "Database",
            schema: Optional[str] = None,
            source: Optional[str] = None,
    ) -> Engine:
        user_name = utils.get_username()
        return database.get_sqla_engine(
            schema=schema, nullpool=True, user_name=user_name, source=source
        )

    @classmethod
    def get_all_datasource_names(
            cls, database: "Database", inspector: Inspector, datasource_type: str
    ) -> List[DatasourceName]:
        """Returns a list of all tables or views in database.

        :param database:
        :param inspector: Sqlalchemy inspector
        :param datasource_type: Datasource_type can be 'table' or 'view'
        :return: List of all datasources in database or schema
        """
        # TODO: Fix circular import caused by importing Database
        schemas = database.get_all_schema_names(
            inspector=inspector,
        )
        all_datasources: List[DatasourceName] = []
        for schema in schemas:
            if datasource_type == "table":
                all_datasources += database.get_all_table_names_in_schema(
                    schema=schema,
                    inspector=inspector

                )
            elif datasource_type == "view":
                all_datasources += database.get_all_view_names_in_schema(
                    schema=schema,

                )
            else:
                raise Exception(f"Unsupported datasource_type: {datasource_type}")
        return all_datasources

    @classmethod
    def _get_fields(cls, cols: List[Dict[str, Any]]) -> List[Any]:
        return [column(c["name"]) for c in cols]

    @classmethod
    def get_view_names(
            cls, database: "Database", inspector: Inspector, schema: Optional[str]
    ) -> List[str]:
        """
        Get all views from schema

        :param database:
        :param inspector: SqlAlchemy inspector
        :param schema: Schema name. If omitted, uses default schema for database
        :return: All views in schema
        """
        views = inspector.get_view_names(schema)
        if schema and cls.try_remove_schema_from_table_name:
            views = [re.sub(f"^{schema}\\.", "", view) for view in views]
        return sorted(views)

    @classmethod
    def get_table_names(
            cls, inspector: Inspector, schema: Optional[str] = None
    ) -> List[str]:
        """
        Get all tables from schema

        :param inspector: SqlAlchemy inspector
        :param schema: Schema to inspect. If omitted, uses default schema for database
        :return: All tables in schema
        """
        tables = inspector.get_table_names(schema)
        if schema and cls.try_remove_schema_from_table_name:
            tables = [re.sub(f"^{schema}\\.", "", table) for table in tables]
        return sorted(tables)

