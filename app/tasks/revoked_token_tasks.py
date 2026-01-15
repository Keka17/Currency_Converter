import datetime
from celery import shared_task
from sqlalchemy import delete
from app.database.database import SessionLocal
from app.models.models import RevokedToken


@shared_task(ignore_results=True)
def cleanup_expired_tokens():
    """
    Periodic task to remove expired JWT tokens from the database.
    Triggered daily by Celery Beat.
    """
    db = SessionLocal()
    try:
        now = datetime.datetime.now(datetime.UTC)
        stmt = delete(RevokedToken).where(RevokedToken.expires_at < now)
        db.execute(stmt)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error during cleanup: {e}")
    finally:
        db.close()
