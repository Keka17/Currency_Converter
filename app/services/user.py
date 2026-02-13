from sqlalchemy import select
from app.database.models import User
from app.exceptions.users import UserNotFoundException


class UserService:
    @staticmethod
    async def get_users(session):
        query = select(User)
        result = await session.execute(query)

        return result.scalars().all()

    @staticmethod
    async def delete_user(user_id: int, admin, session):
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        user_in_db = result.scalars().first()

        if not user_in_db:
            raise UserNotFoundException()

        await session.delete(user_in_db)
        await session.commit()
