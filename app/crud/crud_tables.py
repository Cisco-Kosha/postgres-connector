from app.db.session import *

from app.utils.core import *

db = get_sqlalchemy_db()


class CRUDTables:

    def get_table_properties_by_name(self, name: str, inspector: Inspector) -> List[Dict[str, Any]]:
        return db.get_columns(inspector=inspector, table_name=name)

    def get_tables(self, inspector: Inspector) -> List[Any]:
        return db.db_engine_spec.get_table_names(inspector=inspector)


table = CRUDTables()
