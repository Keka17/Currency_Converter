from .base import AppException


class InvalidCurrencyCodeException(AppException):
    def __init__(self, invalid_codes: list[str]):
        super().__init__(
            status_code=400,
            message=f"Invalid currency code provided: {', '.join(invalid_codes)}",
            error_code="INVALID_CODE",
        )


class EmptyCurrencyCodeException(AppException):
    def __init__(self):
        super().__init__(
            status_code=422,
            message="Missing required query parameter: codes",
            error_code="UNPROCESSABLE_ENTITY",
        )
