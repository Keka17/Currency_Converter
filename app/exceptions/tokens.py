from .base import AppException


class TokenExpiredException(AppException):
    def __init__(self):
        super().__init__(
            status_code=401, message="Token has expired", error_code="TOKEN_EXPIRED"
        )


class InvalidTokenException(AppException):
    def __init__(self):
        super().__init__(
            status_code=401, message="Invalid token", error_code="INVALID_TOKEN"
        )


class InvalidTokenTypeException(AppException):
    def __init__(self, expected_type: str):
        super().__init__(
            status_code=401,
            message=f"Invalid token type. Expected {expected_type}-token .",
            error_code="INVALID_TOKEN_TYPE",
        )


class TokenRevokedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=401,
            message="Token has been revoked",
            error_code="TOKEN_REVOKED",
        )
