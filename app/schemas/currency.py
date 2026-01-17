from pydantic import BaseModel, Field


class Converter(BaseModel):
    code_1: str
    code_2: str
    k: float = Field(default=1, gt=0)  # Only positive float numbers
