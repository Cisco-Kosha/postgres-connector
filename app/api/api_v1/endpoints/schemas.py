from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.core.config import logger
from app.crud import crud_schemas
from app.api.api_v1 import deps

router = APIRouter()


@router.get("/", response_model=List[Any])
def get_schemas():
    logger.info("Getting all schemas for table")
    schemas = crud_schemas.schema.get_schemas()
    if schemas is None:
        raise HTTPException(status_code=404, detail="No Schemas found")
    return [t for t in schemas]
