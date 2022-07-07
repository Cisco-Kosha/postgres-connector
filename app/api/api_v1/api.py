from fastapi import APIRouter

from app.api.api_v1.endpoints import records, tables, schemas, rpc

api_router = APIRouter()

api_router.include_router(tables.router, prefix="/db_tables", tags=["table metadata"])
api_router.include_router(schemas.router, prefix="/schema", tags=["database schema"])
api_router.include_router(rpc.router, prefix="/rpc", tags=["stored procedures"])
api_router.include_router(records.router, prefix="", tags=["table records"])


