from typing import Generator, Any

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.engine.reflection import Inspector
from app.db.session import *

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

SessionLocal = get_session_local(get_sqlalchemy_engine())
db = get_sqlalchemy_db()


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_inspector() -> Any:
    inspector = Inspector.from_engine(get_sqlalchemy_engine()
                                      )
    yield inspector
