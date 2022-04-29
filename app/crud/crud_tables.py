from typing import List, Any, Dict

from app.db.metadata import table_metadata
from app.db.session import settings, Database, db, inspector
from app.schemas.table import Table

from app.utils.core import *


class CRUDTables:

    def get_table_properties_by_name(self, name: str, inspector: Inspector) -> List[Dict[str, Any]]:
        return db.get_columns(inspector=inspector, table_name=name)

    def get_tables(self, inspector: Inspector) -> List[Any]:
        return db.db_engine_spec.get_table_names(inspector=inspector)


table = CRUDTables()
