from typing import Any, List, Optional, Set

from fastapi import APIRouter, Depends, HTTPException, Request, Body
from sqlalchemy.orm import Session

from app.core.config import logger
from app.crud.crud_record import CRUDRecord, run_sql_cmd
from app.db.metadata import table_metadata
from app.models.record import get_table_object
from app.schemas.record import CreateRowFunc, RawSQL
from app.api.api_v1 import deps
from app import crud
from app.utils import exception

router = APIRouter()

RecordCreate = CreateRowFunc()


@router.get("/{table}", response_model=List[Any])
def read_records(
        table: str, skip: int = 0, limit: int = 100, session: Session = Depends(deps.get_db)
):
    if table is None:
        raise HTTPException(status_code=409, detail="Table not set")
    logger.info("Getting all records for table: %s", table)
    table_metadata.set_table(table)
    record = CRUDRecord(get_table_object())
    try:
        records = record.get_records(session=session, skip=skip, limit=limit)
        if records is None:
            raise HTTPException(status_code=404, detail="No Records found")
        return [i.serialize for i in records]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
    logger.info("Getting all records for table %s matching query parameters %s", table, request_args)
    table_metadata.set_table(table)
    record = CRUDRecord(get_table_object())
    if not request_args:
        return "No query parameters supplied"
    try:
        record = record.get_record_by_params(session=session, args=request_args)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
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
    logger.info("Posting a record for table %s with data %s", table, record_in)

    table_metadata.set_table(table)
    try:
        record = CRUDRecord(get_table_object())
        record = record.create_record(db=db, obj_in=record_in)
        return record.serialize
    except exception.InsertRowIntoTable as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/query/raw/sql", response_model=Any)
def run_sql_command(
        sql: RawSQL,
        session: Session = Depends(deps.get_db)) -> Any:
    """
    Run raw sql command.
    """
    try:
        resp = run_sql_cmd(session=session, sql_str=sql)
        return resp
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
    logger.info("Deleting all records for table %s matching query parameters %s", table, request_args)
    table_metadata.set_table(table)
    record = CRUDRecord(get_table_object())
    if request_args:
        try:
            record.delete_records_by_params(session=session, args=request_args)
            return "OK"
        except exception.DeleteRowFromTable as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        return "No query parameters supplied"
