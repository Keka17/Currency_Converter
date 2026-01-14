from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.routers import auth
from app.exceptions.base import AppException
from app.handlers.exceptions import app_exception_handler
from app.handlers.validation_errors import validation_exception_handler
from app.middlewares.logs import loguru_middleware
from loguru import logger
import sys


# Удаляем стандартный обработчик
logger.remove()

# Логи для консоли
logger.add(
    sys.stderr,
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    colorize=True,
)

# Логи разных уровней
logger.add(
    "logs/app.log",
    level="INFO",
    rotation="500 MB",
    retention="10 days",
    enqueue=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
logger.add(
    "logs/warnings.log",
    level="WARNING",
    rotation="10 MB",
    retention="5 day",
    enqueue=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
logger.add(
    "logs/errors.log",
    level="ERROR",
    rotation="10 MB",
    retention="1 day",
    enqueue=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)


app = FastAPI()

app.middleware("http")(loguru_middleware)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "API is running!"}
