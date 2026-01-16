from fastapi.exceptions import RequestValidationError
from fastapi import Request
from fastapi.responses import PlainTextResponse


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Validation error handler
    """
    message = "Validation errors:"
    for error in exc.errors():
        message += f"\nField: {error['loc']}, Error: {error['msg']}"
    return PlainTextResponse(message, status_code=400)
