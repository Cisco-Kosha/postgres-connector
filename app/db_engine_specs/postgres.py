from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Match,
    Optional,
    Pattern,
    Tuple,
    TYPE_CHECKING,
    Union,
)
from sqlalchemy.dialects.postgresql.base import PGInspector
from sqlalchemy.sql.type_api import TypeEngine

from app.db_engine_specs import BaseEngineSpec
from app.utils.core import GenericDataType, ColumnSpec


class PostgresqlEngineSpec(BaseEngineSpec):
    engine = "postgresql"
    engine_aliases = {"postgres"}

    default_driver = "psycopg2"
    sqlalchemy_uri_placeholder = (
        "postgresql://user:password@host:port/dbname[?key=value&key=value...]"
    )
    # https://www.postgresql.org/docs/9.1/libpq-ssl.html#LIBQ-SSL-CERTIFICATES
    encryption_parameters = {"sslmode": "require"}

    max_column_name_length = 63
    try_remove_schema_from_table_name = False

    @classmethod
    def get_table_names(
            cls, inspector: PGInspector, schema: Optional[str] = None
    ) -> List[str]:
        """Need to consider foreign tables for PostgreSQL"""
        tables = inspector.get_table_names(schema)
        tables.extend(inspector.get_foreign_table_names(schema))
        return sorted(tables)

