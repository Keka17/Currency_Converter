from datetime import timedelta

from celery import Celery
from celery.schedules import crontab
from .revoked_token_tasks import cleanup_expired_tokens
from .exchange_rate_api import get_actual_rates
from app.core.config import get_settings

settings = get_settings()
"""
Celery settings for asynchronous task processing and scheduled tasks.

Redis is used as:
- a message broker for task distribution between the application and workers;
- a backendfor storing results, which keeps track of task execution status.
"""
celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.autodiscover_tasks(["app.tasks"])
celery_app.conf.timezone = "UTC"

# Setting for Celery beat
celery_app.conf.beat_schedule = {
    "cleanup-tokens-every-day": {
        "task": cleanup_expired_tokens.name,
        # "schedule": crontab(minute='*')  Launch every minute (for testing)
        "schedule": crontab(hour=0, minute=0),  # Launch every midnight (UTC)
    },
    "exchange_rate_api": {
        "task": get_actual_rates.name,
        # "schedule": crontab(minute='*/2'),  # Launch every 2 minutes (for testing)
        "schedule": timedelta(hours=3),  # Launch every 3 hours
    },
}

# Launch in two terminals
# celery -A app.tasks.celery_app.celery_app worker --loglevel=info
# celery -A app.tasks.celery_app.celery_app beat --loglevel=info

# Cleaning up old tasks
# celery -A app.tasks.celery_app.celery_app purge
