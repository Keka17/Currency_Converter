from database import engine
from app.models.models import Base, User, RevokedToken


def create_tables():
    """
    Creates all tables in the database on SQLAlchemy models.
    """
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)  # equal to 'CREATE TABLE IF NOT EXISTS'
    print("All done! 🧁")


if __name__ == "__main__":
    create_tables()
