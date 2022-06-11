from typing import List, Any

import sqlalchemy
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import ResourceClosedError
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.crud.base import CRUDBase
from app.models.record import *
from app.schemas.record import CreateRowFunc, RawSQL
from app.utils import exception

Record = None
record = None


class CRUDRecord(CRUDBase[Record, Any, None]):

    def create_record(self, db: Session, obj_in: Any) -> Any:
        try:
            obj_in_data = jsonable_encoder(obj_in)
            print(obj_in_data)
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            raise exception.InsertRowIntoTable(e)

    def get_record_by_params(self, session: Session, args: Request) -> List[Record]:
        try:
            query = session.query(self.model)
            print(query)
            for key, value in args.items():
                query = query.filter(getattr(self.model, key) == value)
            return query.all()
        except Exception as e:
            raise Exception(e)

    def delete_records_by_params(self, session: Session, args: Request) -> Record:
        try:
            query = session.query(self.model)
            for key, value in args.items():
                query = query.filter(getattr(self.model, key) == value)
            query.delete()
            return session.commit()
        except Exception as e:
            raise exception.DeleteRowFromTable(e)

    def get_records(self, session: Session, skip: int = 0, limit: int = 100) -> List[Record]:
        try:
            return session.query(self.model).offset(skip).limit(limit).all()
        except Exception as e:
            raise Exception(e)


def run_sql_cmd(session: Session, sql_str: RawSQL) -> Any:
    try:
        rs = session.execute(sql_str.raw_sql)
        try:
            result = [dict(row) for row in rs]
        except ResourceClosedError:
            session.commit()
            return 'OK'
        return result
    except Exception as e:
        raise Exception(e)
