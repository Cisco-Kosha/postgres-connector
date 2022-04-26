from typing import List, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase

from app.db.session import *


class CRUDSchemas:

    db = Database(settings.SQLALCHEMY_DATABASE_URI)
    inspector = Inspector.from_engine(engine)

    def get_schemas(self) -> List[Any]:
        return db.get_all_schema_names(inspector=inspector)


schema = CRUDSchemas()
