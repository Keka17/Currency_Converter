import jwt
from jwt import PyJWTError
import bcrypt
import datetime
from sqlalchemy import select

from app.core.security import create_access_token, create_refresh_token
from app.database.models import User, RevokedToken
from app.exceptions.users import UserAlreadyExistsException, UserNotFoundException
from app.exceptions.auth import InvalidCredentialsException
from app.exceptions.tokens import (
    InvalidTokenException,
    InvalidTokenTypeException,
    TokenRevokedException,
)
from app.core.config import get_settings

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


class AuthService:
    @staticmethod
    async def register(user, session):
        query = select(User).where(User.username == user.username)
        result = await session.execute(query)
        user_in_db = result.scalars().first()

        if user_in_db:
            raise UserAlreadyExistsException()

        password_bytes = bytes(user.password, "utf-8")
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

        new_user = User(username=user.username, hashed_password=hashed.decode("utf-8"))

        session.add(new_user)
        await session.commit()

    @staticmethod
    async def login(user_in, session) -> dict:
        query = select(User).where(User.username == user_in.username)
        result = await session.execute(query)
        user_in_db = result.scalars().first()

        if not user_in_db:
            raise UserNotFoundException()

        if not bcrypt.checkpw(
            user_in.password.encode("utf-8"), user_in_db.hashed_password.encode("utf-8")
        ):
            raise InvalidCredentialsException()

        access_token = create_access_token({"sub": user_in.username})
        refresh_token = create_refresh_token({"sub": user_in.username})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "sub": user_in.username,
        }

    @staticmethod
    async def refresh(x_refresh_token: str, session) -> dict:
        try:
            payload = jwt.decode(x_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        except PyJWTError:
            raise InvalidTokenException()

        if payload.get("token_type") != "refresh":
            raise InvalidTokenTypeException(expected_type="refresh")

            # Check the unique token ID in the revoked token database
        jti = payload.get("jti")

        query = select(RevokedToken).where(RevokedToken.jti == jti)
        result = await session.execute(query)
        is_revoked = result.scalars().first()

        if is_revoked:
            raise TokenRevokedException()

        # Revoke the current refresh token and add it to the database
        expire_timestamp = payload.get("exp")
        revoked_entry = RevokedToken(
            jti=jti,
            expires_at=datetime.datetime.fromtimestamp(
                expire_timestamp, tz=datetime.UTC
            ),
        )

        session.add(revoked_entry)

        # Generate a new pair of tokens
        email = payload.get("sub")
        new_access = create_access_token({"sub": email})
        new_refresh = create_refresh_token({"sub": email})

        await session.commit()

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
        }

    @staticmethod
    async def logout(x_refresh_token: str, session):
        try:
            payload = jwt.decode(x_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

            jti = payload.get("jti")
            exp = payload.get("exp")

            session.add(
                RevokedToken(
                    jti=jti,
                    expires_at=datetime.datetime.fromtimestamp(exp, tz=datetime.UTC),
                )
            )
            await session.commit()
        except:
            raise InvalidTokenException()
