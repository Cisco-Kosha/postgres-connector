from pydantic import BaseModel


class NewFunction(BaseModel):
    function_body: str
