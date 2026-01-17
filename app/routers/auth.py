import jwt
from fastapi import APIRouter, Depends, Header
import bcrypt
import datetime
from jwt import PyJWTError
from starlette.responses import JSONResponse

from app.database.database import get_db_connection
from app.schemas.users import UserCreate, UserLogin, User as UserChema
from app.models.models import RevokedToken, User as UserModel
from app.exceptions.auth import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
    AdminAccessRequired,
)
from app.exceptions.tokens import (
    InvalidTokenException,
    InvalidTokenTypeException,
    TokenRevokedException,
)
from app.dependencies.security import (
    create_access_token,
    create_refresh_token,
    decode_jwt_token,
)

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.dependencies.security import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def create_user(user: UserCreate, db: Session = Depends(get_db_connection)):
    """
    User registration function with storage in the database.
    """
    existing_users = db.execute(select(UserModel.username)).scalars().all()

    if user.username in existing_users:
        raise UserAlreadyExistsException()

    password_bytes = bytes(user.password, "utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    db_user = UserModel(username=user.username, hashed_password=hashed.decode("utf-8"))

    db.add(db_user)
    db.commit()

    return JSONResponse(
        status_code=201, content={"message": "You have successfully registered! 😊"}
    )


def get_user_from_db(username: str, db: Session):
    """
    Retrieving a user from the database by a username.
    """
    return db.query(UserModel).filter(UserModel.username == username).first()


@router.post("/login")
async def login(user_in: UserLogin, db: Session = Depends(get_db_connection)):
    """
    Verifying credentials to get a JWT token.
    """
    user = get_user_from_db(user_in.username, db)

    if not user:
        raise UserNotFoundException()

    if not bcrypt.checkpw(
        user_in.password.encode("utf-8"), user.hashed_password.encode("utf-8")
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


@router.post("/refresh")
async def refresh_token(
    x_refresh_token: str = Header(...), db: Session = Depends(get_db_connection)
):
    """
    Updates a pair of tokens.
    Accepts the old Refresh Token, revokes it (add to the database)
    and generates new Access and Refresh tokens.
    """
    try:
        payload = jwt.decode(x_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except PyJWTError:
        raise InvalidTokenException()

    if payload.get("token_type") != "refresh":
        raise InvalidTokenTypeException(expected_type="refresh")

    # Check the unique token ID in the revoked token database
    jti = payload.get("jti")
    is_revoked = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()

    if is_revoked:
        raise TokenRevokedException()

    # Revoke the current refresh token and add it to the database.
    expire_timestamp = payload.get("exp")
    revoked_entry = RevokedToken(
        jti=jti,
        expires_at=datetime.datetime.fromtimestamp(expire_timestamp, tz=datetime.UTC),
    )
    db.add(revoked_entry)

    # Generate a new pair of tokens
    username = payload.get("sub")
    new_access = create_access_token({"sub": username})
    new_refresh = create_refresh_token({"sub": username})

    db.commit()

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(
    x_refresh_token: str = Header(...), db: Session = Depends(get_db_connection)
):
    """
    Ends the user session.
    Retrieves the JTI from the current token and adds it to the database.
    """
    try:
        payload = jwt.decode(x_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        jti = payload.get("jti")
        exp = payload.get("exp")

        # Add the refresh token to the blacklist
        db.add(
            RevokedToken(
                jti=jti,
                expires_at=datetime.datetime.fromtimestamp(exp, tz=datetime.UTC),
            )
        )
        db.commit()
    except:
        raise InvalidTokenException()

    return {"message": "Logged out successfully"}


def get_current_user(
    payload: dict = Depends(decode_jwt_token), db: Session = Depends(get_db_connection)
):
    """
    Retrieves the profile of the currently authenticated user by decoding JWT token.
    Only accessible with a valid Access Token in the Authorization header.
    """
    if payload.get("token_type") != "access":
        raise InvalidTokenTypeException(expected_type="access")

    username: str = payload.get("sub")

    if not username:
        raise InvalidTokenException()

    user = get_user_from_db(username, db)

    if not user:
        raise UserNotFoundException()

    return user


def admin_required(current_user: UserModel = Depends(get_current_user)):
    """
    Check if the authenticated user has the 'is_admin' flag set to True.
    """
    if not current_user.is_admin:
        raise AdminAccessRequired()

    return current_user


@router.get("/users", response_model=list[UserChema])
async def get_users(
    skip: int = 0,
    limit: int = 15,
    db: Session = Depends(get_db_connection),
    admin: UserModel = Depends(admin_required),
):
    """
    Extract all users from the database.
    This endpoint is allowed to users with administrative privileges only.
    Query parameters: skip, limit.
    """
    return db.query(UserModel).offset(skip).limit(limit).all()
