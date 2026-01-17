from .base import AppException


class UserNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=404, message="User not found", error_code="NOT FOUND"
        )


class UserAlreadyExistsException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409, message="User already exists", error_code="CONFLICT"
        )


class InvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__(
            status_code=401, message="Invalid credentials", error_code="UNAUTHORIZED"
        )


class AdminAccessRequired(AppException):
    def __init__(self):
        super().__init__(
            status_code=403, message="Forbidden: admin access required", error_code="FORBIDDEN"
        )