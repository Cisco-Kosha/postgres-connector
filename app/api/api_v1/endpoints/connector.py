from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException

from fastapi.responses import JSONResponse
from pydantic import PostgresDsn
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from fastapi import Request

from app.core.config import settings
from app.db.core import Database

router = APIRouter()


@router.get("/list", response_model=Any)
def get_connector_spec():
    return JSONResponse({"DB_USER": "Database username", "DB_PASSWORD": "Database password",
                         "DB_SERVER": "Database Host", "DB_NAME": "Database name"})


@router.post("/check", response_model=Any)
async def check_connector_spec(request: Request):
    data = await request.json()
    if data is not None:
        db_url = PostgresDsn.build(
            scheme="postgres",
            user=data["DB_USER"],
            password=data["DB_PASSWORD"],
            host=data["DB_SERVER"],
            path=f'/{data["DB_NAME"] or ""}',
        )
        engine = create_engine(db_url, pool_pre_ping=True)
        Inspector = inspect(engine)
        db = Database(settings.SQLALCHEMY_DATABASE_URI)
        inspector = Inspector.from_engine(engine)
        if db.get_schema_names(inspector=inspector) is not None:
            return True
        else:
            return False
    return False
