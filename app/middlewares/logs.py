from fastapi import Request
from loguru import logger
import time


async def loguru_middleware(request: Request, call_next):
    """Middleware для логирования запросов и ответов с помощью Loguru."""
    start_time = time.perf_counter()
    logger.info(f"Received request: {request.method} {request.url.path}")

    response = await call_next(request)  # Выполняем основной запрос

    process_time = time.perf_counter() - start_time
    logger.info(f"Response status: {response.status_code}, Time: {process_time:.4f}s")

    return response
