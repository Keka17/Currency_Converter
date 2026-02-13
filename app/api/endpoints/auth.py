from fastapi import APIRouter, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.database.database import get_db_connection
from app.api.schemas.users import UserCreate

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
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Verifying credentials to get a JWT token.
    """
    return await AuthService.login(form_data, session)


@router.post("/refresh")
async def refresh(
    x_refresh_token: str = Header(...),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Updating a pair of tokens. The refresh token in the headers required. \n\n
    After that, the used token is revoked and added in the database.
    """
    return await AuthService.refresh(x_refresh_token, session)


@router.post("/logout")
async def logout(
    x_refresh_token: str = Header(...),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    User logout from the system. The refresh token in the headers required. \n\n
    After that, the used token is revoked and added in the database.
    """
    await AuthService.logout(x_refresh_token, session)

    return {"message": "Logged out successfully."}
