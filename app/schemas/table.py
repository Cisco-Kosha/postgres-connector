from typing import Optional, Any

from pydantic import BaseModel


class TableBase(BaseModel):
    name: Optional[str]


# Properties to return to client
class Table(TableBase):
    pass
