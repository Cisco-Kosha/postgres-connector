from typing import Optional, Any

from pydantic import BaseModel


# Properties to receive on table row creation
def CreateRowFunc():
    class Row(BaseModel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            for arg in kwargs.copy():
                val = kwargs.pop(arg)
                object.__setattr__(self, arg, val)
    return Row


class RawSQL(BaseModel):
    raw_sql: str = None
