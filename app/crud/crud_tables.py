from typing import List, Any, Dict

from app.db.metadata import table_metadata
from app.db.session import settings, Database
from app.schemas.table import Table

from app.utils.core import *


class CRUDTables:
    db = Database(settings.SQLALCHEMY_DATABASE_URI)

    def get_table_properties_by_name(self, name: str, inspector: Inspector) -> List[Dict[str, Any]]:
        return self.db.get_columns(inspector=inspector, table_name=name)

    def get_tables(self, inspector: Inspector) -> List[Any]:
        return self.db.db_engine_spec.get_table_names(inspector=inspector)

    def set_table(self, table: Table) -> str:
        table_metadata.set_table(table.name)
        set_record_class()
        return "OK"


table = CRUDTables()
