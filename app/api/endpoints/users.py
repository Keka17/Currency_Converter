from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db_connection
from app.database.models import User as UserModel
from app.api.schemas.users import User as UserSchema
from app.services.user import UserService
from app.dependencies.dependencies import admin_required, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/user_info", response_model=UserSchema)
async def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    return current_user


@router.get("/list", response_model=list[UserSchema])
async def get_users(
    session: AsyncSession = Depends(get_db_connection),
    admin: UserModel = Depends(admin_required),
):
    return await UserService.get_users(session)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    admin: UserModel = Depends(admin_required),
    session: AsyncSession = Depends(get_db_connection),
):
    await UserService.delete_user(user_id, admin, session)

    return {"message": f"User with id {user_id} was deleted successfully."}
