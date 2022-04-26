# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Utility functions used across Superset"""
import collections
import decimal
import errno
import json
import logging
import os
import platform
import re
import signal
import smtplib
import tempfile
import threading
import traceback
import uuid
import zlib
from datetime import date, datetime, time, timedelta
from distutils.util import strtobool
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from enum import Enum, IntEnum
from timeit import default_timer
from types import TracebackType
from typing import (
    Any,
    Callable,
    cast,
    Dict,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TYPE_CHECKING,
    TypeVar,
    Union,
)
from urllib.parse import unquote_plus

from sqlalchemy import event, exc, select, Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.sql.type_api import Variant
from sqlalchemy.types import TEXT, TypeDecorator, TypeEngine
from typing_extensions import TypedDict, TypeGuard

import _thread  # pylint: disable=C0411


try:
    from pydruid.utils.having import Having
except ImportError:
    pass


logging.getLogger("MARKDOWN").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

DTTM_ALIAS = "__timestamp"

NO_TIME_RANGE = "No filter"

TIME_COMPARISION = "__"

JS_MAX_INTEGER = 9007199254740991  # Largest int Java Script can handle 2^53-1

InputType = TypeVar("InputType")


class LenientEnum(Enum):
    """Enums with a `get` method that convert a enum value to `Enum` if it is a
    valid value."""

    @classmethod
    def get(cls, value: Any) -> Any:
        try:
            return super().__new__(cls, value)
        except ValueError:
            return None


class AdhocMetricExpressionType(str, Enum):
    SIMPLE = "SIMPLE"
    SQL = "SQL"

class DatasourceName(NamedTuple):
    table: str
    schema: str

class AnnotationType(str, Enum):
    FORMULA = "FORMULA"
    INTERVAL = "INTERVAL"
    EVENT = "EVENT"
    TIME_SERIES = "TIME_SERIES"


class GenericDataType(IntEnum):
    """
    Generic database column type that fits both frontend and backend.
    """

    NUMERIC = 0
    STRING = 1
    TEMPORAL = 2
    BOOLEAN = 3
    # ARRAY = 4     # Mapping all the complex data types to STRING for now
    # JSON = 5      # and leaving these as a reminder.
    # MAP = 6
    # ROW = 7


class ChartDataResultFormat(str, Enum):
    """
    Chart data response format
    """

    CSV = "csv"
    JSON = "json"


class ChartDataResultType(str, Enum):
    """
    Chart data response type
    """

    COLUMNS = "columns"
    FULL = "full"
    QUERY = "query"
    RESULTS = "results"
    SAMPLES = "samples"
    TIMEGRAINS = "timegrains"
    POST_PROCESSED = "post_processed"


class DatasourceDict(TypedDict):
    type: str
    id: int



class ExtraFiltersTimeColumnType(str, Enum):
    GRANULARITY = "__granularity"
    TIME_COL = "__time_col"
    TIME_GRAIN = "__time_grain"
    TIME_ORIGIN = "__time_origin"
    TIME_RANGE = "__time_range"


class ExtraFiltersReasonType(str, Enum):
    NO_TEMPORAL_COLUMN = "no_temporal_column"
    COL_NOT_IN_DATASOURCE = "not_in_datasource"
    NOT_DRUID_DATASOURCE = "not_druid_datasource"


class FilterOperator(str, Enum):
    """
    Operators used filter controls
    """

    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUALS = ">="
    LESS_THAN_OR_EQUALS = "<="
    LIKE = "LIKE"
    ILIKE = "ILIKE"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"
    IN = "IN"  # pylint: disable=invalid-name
    NOT_IN = "NOT IN"
    REGEX = "REGEX"
    IS_TRUE = "IS TRUE"
    IS_FALSE = "IS FALSE"


class PostProcessingBoxplotWhiskerType(str, Enum):
    """
    Calculate cell contribution to row/column total
    """

    TUKEY = "tukey"
    MINMAX = "min/max"
    PERCENTILE = "percentile"


class PostProcessingContributionOrientation(str, Enum):
    """
    Calculate cell contribution to row/column total
    """

    ROW = "row"
    COLUMN = "column"


class QueryMode(str, LenientEnum):
    """
    Whether the query runs on aggregate or returns raw records
    """

    RAW = "raw"
    AGGREGATE = "aggregate"


class QuerySource(Enum):
    """
    The source of a SQL query.
    """

    CHART = 0
    DASHBOARD = 1
    SQL_LAB = 2


class QueryStatus(str, Enum):  # pylint: disable=too-few-public-methods
    """Enum-type class for query statuses"""

    STOPPED: str = "stopped"
    FAILED: str = "failed"
    PENDING: str = "pending"
    RUNNING: str = "running"
    SCHEDULED: str = "scheduled"
    SUCCESS: str = "success"
    FETCHING: str = "fetching"
    TIMED_OUT: str = "timed_out"


class DashboardStatus(str, Enum):
    """Dashboard status used for frontend filters"""

    PUBLISHED = "published"
    DRAFT = "draft"


class RowLevelSecurityFilterType(str, Enum):
    REGULAR = "Regular"
    BASE = "Base"


class TimeRangeEndpoint(str, Enum):
    """
    The time range endpoint types which represent inclusive, exclusive, or unknown.

    Unknown represents endpoints which are ill-defined as though the interval may be
    [start, end] the filter may behave like (start, end] due to mixed data types and
    lexicographical ordering.

    :see: https://github.com/apache/superset/issues/6360
    """

    EXCLUSIVE = "exclusive"
    INCLUSIVE = "inclusive"
    UNKNOWN = "unknown"


class TemporalType(str, Enum):
    """
    Supported temporal types
    """

    DATE = "DATE"
    DATETIME = "DATETIME"
    SMALLDATETIME = "SMALLDATETIME"
    TEXT = "TEXT"
    TIME = "TIME"
    TIMESTAMP = "TIMESTAMP"


class ColumnTypeSource(Enum):
    GET_TABLE = 1
    CURSOR_DESCRIPION = 2


class ColumnSpec(NamedTuple):
    sqla_type: Union[TypeEngine, str]
    generic_type: GenericDataType
    is_dttm: bool
    python_date_format: Optional[str] = None


try:
    # Having might not have been imported.
    class DimSelector(Having):
        def __init__(self, **args: Any) -> None:
            # Just a hack to prevent any exceptions
            Having.__init__(self, type="equalTo", aggregation=None, value=None)

            self.having = {
                "having": {
                    "type": "dimSelector",
                    "dimension": args["dimension"],
                    "value": args["value"],
                }
            }


except NameError:
    pass
