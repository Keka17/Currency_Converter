from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import decode_jwt_token
from app.exceptions.users import (
    UserNotFoundException,
    AdminAccessRequired,
)
from app.exceptions.tokens import InvalidTokenTypeException
from app.database.models import User as UserModel
from app.database.database import get_db_connection


async def get_current_user(
    payload: dict = Depends(decode_jwt_token),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Retrieves the profile of the current user by decoding JWT token.
    Only accessible with a valid Access Token in the Authorization header.
    """
    if payload.get("token_type") != "access":
        raise InvalidTokenTypeException(expected_type="access")

    username: str = payload.get("sub")

    query = select(UserModel).where(UserModel.username == username)
    result = await session.execute(query)
    user_in_db = result.scalars().first()

    if not user_in_db:
        raise UserNotFoundException()

    return user_in_db


async def admin_required(current_user: UserModel = Depends(get_current_user)):
    """
    Check if the authenticated user has the 'is_admin' flag set to True.
    """
    if not current_user.is_admin:
        raise AdminAccessRequired()

    return current_user
