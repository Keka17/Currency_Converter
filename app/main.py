from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from app.api.endpoints import users, currency, auth
from app.exceptions.base import AppException
from app.handlers.exceptions import app_exception_handler
from app.handlers.validation_errors import validation_exception_handler
from app.middlewares.logs import loguru_middleware
from loguru import logger
import sys

# Remove the default logger
logger.remove()

# Console logs
logger.add(
    sys.stderr,
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    colorize=True,
)

# Different levels logs
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


app = FastAPI(
    title="Currency Converter API",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # Hide models section by default
        "docExpansion": "none",  # Collapse all sections by default,
        "displayRequestDuration": True,
        "tryItOutEnabled": True,
        "persistAuthorization": True,
    },
)

templates = Jinja2Templates(directory="app/templates")

app.middleware("http")(loguru_middleware)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(users.router)
app.include_router(currency.router)
app.include_router(auth.router)


@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")
