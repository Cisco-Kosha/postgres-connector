import logging

import sqlalchemy as sqla
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type

from sqlalchemy import (
    Boolean,
    Column,
    create_engine,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
)
from sqlalchemy.engine import Dialect, Engine, url
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.engine.url import make_url, URL
from sqlalchemy.exc import ArgumentError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.pool import NullPool
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql import expression, Select

from app import db_engine_specs

from app.utils.core import *

logger = logging.getLogger(__name__)


class Database(object):
    sqlalchemy_uri = None
    driver_name = None
    host = None
    db_name = None
    port = None
    username = None
    password = None

    def __init__(self, sqlalchemy_uri):
        self.sqlalchemy_uri = sqlalchemy_uri



    @property
    def sqlalchemy_uri_decrypted(self) -> str:
        try:
            conn = sqla.engine.url.make_url(self.sqlalchemy_uri)
        except (ArgumentError, ValueError):
            # if the URI is invalid, ignore and return a placeholder url
            # (so users see 500 less often)
            return "dialect://invalid_uri"
        conn.password = self.password
        return str(conn)

    @property
    def backend(self) -> str:
        sqlalchemy_url = make_url(self.sqlalchemy_uri_decrypted)
        return sqlalchemy_url.get_backend_name()  # pylint: disable=no-member

    @property
    def db_engine_spec(self) -> Type[db_engine_specs.BaseEngineSpec]:
        return self.get_db_engine_spec_for_backend(self.backend)

    @classmethod
    def get_db_engine_spec_for_backend(
            cls, backend: str
    ) -> Type[db_engine_specs.BaseEngineSpec]:
        engines = db_engine_specs.get_engine_specs()
        return engines.get(backend, db_engine_specs.BaseEngineSpec)

    def get_table(self, table_name: str, schema: Optional[str] = None) -> Table:
        extra = self.get_extra()
        meta = MetaData(**extra.get("metadata_params", {}))
        return Table(
            table_name,
            meta,
            schema=schema or None,
            autoload=True,
            autoload_with=self.get_sqla_engine(),
        )

    def get_extra(self) -> Dict[str, Any]:
        return "self.db_engine_spec.get_extra_params(self)"

    def get_sqla_engine(
        self,
        schema: Optional[str] = None,
        nullpool: bool = True,
        user_name: Optional[str] = None,
        source: Optional[QuerySource] = None,
    ) -> Engine:
        extra = self.get_extra()
        sqlalchemy_url = make_url(self.sqlalchemy_uri)

        return create_engine(sqlalchemy_url)

    def get_all_table_names_in_database(
        self,
        cache: bool = False,
        cache_timeout: Optional[bool] = None,
        force: bool = False,
    ) -> List[DatasourceName]:
        return self.db_engine_spec.get_all_datasource_names(self, inspector=self.inspector, datasource_type="table")

    @property
    def inspector(self) -> Inspector:
        engine = self.get_sqla_engine()
        return sqla.inspect(engine)

    def get_all_table_names_in_schema(
        self,
        schema: str,
        inspector: Inspector,
        cache: bool = False,
        cache_timeout: Optional[int] = None,
        force: bool = False,
    ) -> List[DatasourceName]:
        """Parameters need to be passed as keyword arguments.

        For unused parameters, they are referenced in
        cache_util.memoized_func decorator.

        :param inspector:
        :param schema: schema name
        :param cache: whether cache is enabled for the function
        :param cache_timeout: timeout in seconds for the cache
        :param force: whether to force refresh the cache
        :return: list of tables
        """
        try:
            tables = self.db_engine_spec.get_table_names(
                inspector=inspector, schema=schema
            )
            return [
                DatasourceName(table=table, schema=schema) for table in tables
            ]
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning(ex)
            return []

    @classmethod
    def get_columns(
            cls, inspector: Inspector, table_name: str, schema: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all columns from a given schema and table

        :param inspector: SqlAlchemy Inspector instance
        :param table_name: Table name
        :param schema: Schema name. If omitted, uses default schema for database
        :return: All columns in table
        """
        return inspector.get_columns(table_name, schema)

    def get_all_schema_names(
        self,
        inspector: Inspector,
        cache: bool = False,
        cache_timeout: Optional[int] = None,
        force: bool = False,
    ) -> List[str]:
        """Parameters need to be passed as keyword arguments.

        For unused parameters, they are referenced in
        cache_util.memoized_func decorator.

        :param inspector:
        :param cache: whether cache is enabled for the function
        :param cache_timeout: timeout in seconds for the cache
        :param force: whether to force refresh the cache
        :return: schema list
        """
        return self.get_schema_names(inspector)

    @classmethod
    def get_schema_names(cls, inspector: Inspector) -> List[str]:
        """
        Get all schemas from database

        :param inspector: SqlAlchemy inspector
        :return: All schemas in the database
        """
        return sorted(inspector.get_schema_names())

    def get_all_view_names_in_schema(
        self,
        schema: str,
        cache: bool = False,
        cache_timeout: Optional[int] = None,
        force: bool = False,
    ) -> List[DatasourceName]:
        """Parameters need to be passed as keyword arguments.

        For unused parameters, they are referenced in
        cache_util.memoized_func decorator.

        :param schema: schema name
        :param cache: whether cache is enabled for the function
        :param cache_timeout: timeout in seconds for the cache
        :param force: whether to force refresh the cache
        :return: list of views
        """
        try:
            views = self.db_engine_spec.get_view_names(
                database=self, inspector=self.inspector, schema=schema
            )
            return [DatasourceName(table=view, schema=schema) for view in views]
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning(ex)
            return []

