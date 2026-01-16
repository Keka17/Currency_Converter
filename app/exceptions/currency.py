from .base import AppException


class InvalidCurrencyCodeException(AppException):
    def __init__(self):
        super().__init__(
            status_code=400,
            message="Currency code is invalid",
            error_code="INVALID_CODE",
        )
