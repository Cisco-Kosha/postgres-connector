from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.orm import Session

from app import schemas
from app import crud
from app.core.config import logger
from app.schemas.table import Table
from app.api.api_v1 import deps
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/list", response_model=List[Any])
def get_tables(table = Depends(crud.crud_tables.CRUDTables),
               inspector: Inspector = Depends(deps.get_inspector)):
    tables = table.get_tables(inspector)
    if tables is None:
        raise HTTPException(status_code=404, detail="No Tables found")
    return [t for t in tables]


@router.get("/get/{name}", response_model=Any)
def get_table_columns(name: str, table = Depends(crud.crud_tables.CRUDTables),
                      inspector: Inspector = Depends(deps.get_inspector)):
    table_columns = table.get_table_properties_by_name(name, inspector)
    if table_columns is None:
        raise HTTPException(status_code=404, detail="No Columns found")
    return JSONResponse(str(table_columns))
