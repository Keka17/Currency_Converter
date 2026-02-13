from pydantic import BaseModel, Field, ConfigDict


# Example for documentation
def example_query(schema: dict) -> None:
    schema["example"] = {"code_1": "eur", "code_2": "rub", "k": 10.5}


class Converter(BaseModel):
    code_1: str
    code_2: str
    k: float = Field(default=1, gt=0)  # Only positive float numbers

    model_config = ConfigDict(json_schema_extra=example_query)
