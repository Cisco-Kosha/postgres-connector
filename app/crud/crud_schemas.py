from typing import List, Any

from app.db.session import get_sqlalchemy_db, get_inspector, get_sqlalchemy_engine

db = get_sqlalchemy_db()
inspector = get_inspector(engine=get_sqlalchemy_engine())


class CRUDSchemas:

    def get_schemas(self) -> List[Any]:
        return db.get_all_schema_names(inspector=inspector)


schema = CRUDSchemas()
