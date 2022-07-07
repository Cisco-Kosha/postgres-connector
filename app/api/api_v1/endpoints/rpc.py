import json
from typing import Any, List

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import ResourceClosedError
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.core.config import logger
from app.api.api_v1 import deps
from app.db.session import Base
from app.schemas.rpc import NewFunction
from sqlalchemy.schema import DDL
from sqlalchemy import func

router = APIRouter()


@router.get("/list", response_model=Any)
def get_user_defined_function(
        session: Session = Depends(deps.get_db)) -> Any:
    """
    Create or replace user defined functions
    """
    rs = session.execute("SELECT routines.routine_name, parameters.data_type, parameters.ordinal_position " +
                         " FROM information_schema.routines " +
                         " LEFT JOIN information_schema.parameters ON routines.specific_name=parameters.specific_name " +
                         " WHERE routines.specific_schema='public' " +
                         " ORDER BY routines.routine_name, parameters.ordinal_position;")
    try:
        result = [dict(row) for row in rs]
    except Exception as e:
        return e
    return result


@router.post("/create", response_model=Any)
def create_user_defined_function(
        function: NewFunction,
        session: Session = Depends(deps.get_db)) -> Any:
    """
    Create or replace user defined functions
    """
    rs = session.execute(function.function_body)
    session.commit()
    try:
        result = [dict(row) for row in rs]
    except Exception as e:
        return e
    return result


@router.post("/{name}", response_model=Any)
async def execute_rpc_function(name: str, request: Request, session: Session = Depends(deps.get_db)) -> Any:
    """
    Execute user defined function
    :param request:
    :param name: name of the function
    :param session:
    :return: Tuple output
    """
    t = ()
    data_json = await request.json()
    for key, value in data_json.items():
        print(value)
        t += (int(value),)
    print(t)
    data = session.query(getattr(func.public, name)(*t)).all()
    return data


@router.delete("/{name}", response_model=Any)
def delete_user_defined_function( name: str,
        session: Session = Depends(deps.get_db)) -> Any:
    """
    Delete user defined functions
    """
    rs = session.execute("DROP FUNCTION IF EXISTS " + name)
    session.commit()
    try:
        result = [dict(row) for row in rs]
    except Exception as e:
        return e
    return result
