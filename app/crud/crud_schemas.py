from typing import List, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.api_v1.deps import get_inspector
from app.crud.base import CRUDBase

from app.db.session import db, inspector


class CRUDSchemas:

    inspector = get_inspector()

    def get_schemas(self) -> List[Any]:
        return db.get_all_schema_names(inspector=inspector)


schema = CRUDSchemas()
