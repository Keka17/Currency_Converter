from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()


engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_connection():
    """
    Opening a connection to the database, executing a query
    and immidiately closing it.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
