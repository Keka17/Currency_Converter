from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions.base import AppException
from app.schemas.errors import ErrorResponse


async def app_exception_handler(request: Request, exc: AppException):
    """
    Global Exception Handler
    """
    error_response = ErrorResponse(
        status_code=exc.status_code, message=exc.message, error_code=exc.error_code
    )

    return JSONResponse(
        status_code=exc.status_code, content=error_response.model_dump()
    )
