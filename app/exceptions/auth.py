from .base import AppException


class InvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__(
            status_code=401,
            message="Invalid credentials",
            error_code="INVALID_CREDENTIALS",
        )
