from fastapi import APIRouter

from app.api.api_v1.endpoints import records, tables, schemas

api_router = APIRouter()

api_router.include_router(records.router, prefix="", tags=["records"])
api_router.include_router(tables.router, prefix="/table", tags=["table"])
api_router.include_router(schemas.router, prefix="/schema", tags=["schema"])

