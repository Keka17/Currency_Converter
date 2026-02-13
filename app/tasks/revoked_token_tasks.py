import asyncio
import datetime
from celery import shared_task
from sqlalchemy import delete
from app.database.database import AsyncSessionLocal
from app.database.models import RevokedToken


async def sql_request():
    """
    Asynchronous function to perform sql-delete operation.
    """

    async with AsyncSessionLocal() as session:
        try:
            now = datetime.datetime.now(datetime.UTC)
            query = delete(RevokedToken).where(RevokedToken.expires_at < now)
            await session.execute(query)
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"Error during cleanup: {e}")


@shared_task(ignore_results=True)
def cleanup_expired_tokens():
    """
    Periodic task to remove expired JWT tokens from the database.
    Triggered daily by Celery Beat.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sql_request())
