from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.database.database import get_db_connection
from app.api.schemas.users import UserCreate, UserLogin

from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def create_user(
    user: UserCreate, session: AsyncSession = Depends(get_db_connection)
):
    """
    User registration function with storage in the database.
    """
    await AuthService.register(user, session)

    return JSONResponse(
        status_code=201, content={"message": "You have successfully registered! 😊"}
    )


@router.post("/login")
async def login(user: UserLogin, session: AsyncSession = Depends(get_db_connection)):
    """
    Verifying credentials to get a JWT token.
    """
    return await AuthService.login(user, session)


@router.post("/refresh")
async def refresh(
    x_refresh_token: str = Header(...),
    session: AsyncSession = Depends(get_db_connection),
):
    return await AuthService.refresh(x_refresh_token, session)


@router.post("/logout")
async def logout(
    x_refresh_token: str = Header(...),
    session: AsyncSession = Depends(get_db_connection),
):
    await AuthService.logout(x_refresh_token, session)

    return {"message": "Logged out successfully."}
