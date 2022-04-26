from typing import Any, List, Optional, Set

from fastapi import APIRouter, Depends, HTTPException, Request, Body
from sqlalchemy.orm import Session

from app.crud.crud_record import CRUDRecord
from app.db.metadata import table_metadata
from app.models.record import get_table_object
from app.schemas.record import CreateRowFunc, RawSQL
from app.api.api_v1 import deps
from app import crud

router = APIRouter()

RecordCreate = CreateRowFunc()


@router.get("/{table}", response_model=List[Any])
def read_records(
        table: str, skip: int = 0, limit: int = 100, session: Session = Depends(deps.get_db)
):
    if table is None:
        raise HTTPException(status_code=409, detail="Table not set")
    table_metadata.set_table(table)
    record = CRUDRecord(get_table_object())
    records = record.get_records(session=session, skip=skip, limit=limit)
    if records is None:
        raise HTTPException(status_code=404, detail="No Records found")
    return [i.serialize for i in records]


@router.get("/{table}/query", response_model=Any)
def read_records_by_query_params(table: str, req: Request,
                                 session: Session = Depends(deps.get_db),
                                 ):
    """
    Read records by supplying variable parameters (similar to where clause) i.e. key1=value1&key2=value2
    """

    request_args = dict(req.query_params)
    if table is None:
        raise HTTPException(status_code=409, detail="Table not set")
    table_metadata.set_table(table)
    record = CRUDRecord(get_table_object())
    if not request_args:
        return "No query parameters supplied"
    record = record.get_record_by_params(session=session, args=request_args)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.post("/{table}", response_model=Any)
def create_record(table: str,
                  *,
                  db: Session = Depends(deps.get_db),
                  record_in: RecordCreate) -> Any:
    """
    Create new record.
    """
    if table is None:
        raise HTTPException(status_code=409, detail="Table not set")
    table_metadata.set_table(table)
    record = CRUDRecord(get_table_object())
    record = record.create_record(db=db, obj_in=record_in)
    return record.serialize


@router.post("/{table}/query", response_model=Any)
def run_sql_command(
        table: str,
        sql: RawSQL,
        session: Session = Depends(deps.get_db)) -> Any:
    """
    Run raw sql command.
    """
    if table is None:
        raise HTTPException(status_code=409, detail="Table not set")
    table_metadata.set_table(table)
    resp = crud.crud_record.run_sql_cmd(session=session, sql_str=sql)
    return resp


@router.delete("/{table}", response_model=Any)
def delete_record(table: str,
                  req: Request,
                  session: Session = Depends(deps.get_db)):
    """
    Delete record by supplying variable parameters (similar to where clause) i.e. key1=value1&key2=value2
    """
    request_args = dict(req.query_params)
    if table is None:
        raise HTTPException(status_code=409, detail="Table not set")
    table_metadata.set_table(table)
    record = CRUDRecord(get_table_object())
    if request_args:
        record.delete_records_by_params(session=session, args=request_args)
        return "OK"
    else:
        return "No query parameters supplied"
