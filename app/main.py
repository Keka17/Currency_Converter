from fastapi import FastAPI

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


@app.get("/")
def root():
    return {"message": "API is running!"}
