from fastapi import APIRouter, Depends
import bcrypt
from starlette.responses import JSONResponse

from app.database.database import get_db_connection
from app.schemas.users import UserCreate, UserLogin, User as UserChema
from app.models.models import User as UserModel
from app.exceptions.users import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
)

from sqlalchemy.orm import Session
from sqlalchemy import select

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

    return JSONResponse(status_code=200, content="You have successfully registered! 😊")


@router.get("/users", response_model=list[UserChema])
async def get_users(
    skip: int = 0, limit: int = 15, db: Session = Depends(get_db_connection)
):
    """
    Extract all users from the database.
    Query parameters: skip, limit.
    """
    return db.query(UserModel).offset(skip).limit(limit).all()
