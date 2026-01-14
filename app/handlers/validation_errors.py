from fastapi.exceptions import RequestValidationError
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from app.schemas.errors import ValidationErrorItem, ValidationErrorResponse


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Validation error handler
    """
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )
