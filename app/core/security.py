import jwt
import uuid
import datetime
from datetime import timedelta
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.exceptions.tokens import TokenExpiredException, InvalidTokenException
from app.core.config import get_settings

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


def create_jwt_token(
    data: dict, expires_delta: timedelta, token_type: str, include_jti: bool = False
):
    """
    Function for creating a JWT token. It copies the input data,
    adds the expiration time, and encodes the token.
    """
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + expires_delta

    payload = {"exp": expire, "token_type": token_type, **to_encode}

    # JTI for refresh tokens
    if include_jti:
        payload["jti"] = str(uuid.uuid4())

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict):
    """Creates access-type JWT token"""
    return create_jwt_token(
        data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), "access"
    )


def create_refresh_token(data: dict):
    """Creates refresh-type JWT token"""
    return create_jwt_token(
        data,
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh",
        include_jti=True,
    )


# Extracts the token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def decode_jwt_token(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Extracts user information from the access token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except jwt.InvalidTokenError:
        raise InvalidTokenException()
