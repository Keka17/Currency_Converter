from celery import Celery
from celery.schedules import crontab
from .revoked_token_tasks import cleanup_expired_tokens

"""
Celery settings for asynchronous task processing and scheduled tasks.

Redis is used as:
- a message broker for task distribution between the application and workers;
- a backendfor storing results, which keeps track of task execution status.
"""
celery_app = Celery(
    "worker", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)

celery_app.autodiscover_tasks(["app.tasks"])
celery_app.conf.timezone = "UTC"

# Setting for Celery beat
celery_app.conf.beat_schedule = {
    "cleanup-tokens-every-day": {
        "task": cleanup_expired_tokens.name,
        # "schedule": crontab(minute='*')  Launch every minute (for testing)
        "schedule": crontab(hour=0, minute=0),  # Launch every midnight (UTC)
    }
}

# Launch in two terminals
# celery -A app.tasks.celery_app.celery_app worker --loglevel=info
# celery -A app.tasks.celery_app.celery_app beat --loglevel=info

# Cleaning up old tasks
# celery -A app.tasks.celery_app.celery_app purge
