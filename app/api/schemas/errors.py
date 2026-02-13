from pydantic import BaseModel


class ErrorResponse(BaseModel):
    status_code: int
    message: str
    error_code: str


class ValidationErrorItem(BaseModel):
    field: str
    message: str


class ValidationErrorResponse(BaseModel):
    detail: list[ValidationErrorItem]
