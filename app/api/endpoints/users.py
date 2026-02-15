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
    """
    Getting information about the current authenticated user.  \n
    **Protected endpoint**: a valid access token in the Authorization header required.
    """
    return current_user


@router.get("/list", response_model=list[UserSchema])
async def get_users(
    session: AsyncSession = Depends(get_db_connection),
    admin: UserModel = Depends(admin_required),
):
    """
    Getting a list of all registered users.  \n
    **Protected** endpoint with strict access rights: only available to the admin.
    """
    return await UserService.get_users(session)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    admin: UserModel = Depends(admin_required),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Deleting of a specific user by their id. \n
    **Protected** endpoint with strict access rights: only available to the admin.
    """
    await UserService.delete_user(user_id, admin, session)

    return {"message": f"User with id {user_id} was deleted successfully."}
