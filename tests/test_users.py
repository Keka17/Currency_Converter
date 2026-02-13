import asyncio
from sqlalchemy import select
from app.database.models import User
from tests.conftest import client, async_session
from tests.utils import add_users

from app.core.security import (
    create_access_token,
    create_refresh_token,
)


async def test_get_users_access_control(client, async_session):
    """
    Testing endpoint access control (admin only).
    Endpoint GET /users/list.
    """
    await add_users(async_session)

    # Admin (Aragorn II)
    admin_token = create_access_token({"sub": "Aragorn II"}).decode("utf-8")
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    response_admin = await client.get("/users/list", headers=headers_admin)

    assert response_admin.status_code == 200
    assert len(response_admin.json()) == 3

    # Error: refresh token
    admin_refresh_token = create_refresh_token({"sub": "Aragorn II"}).decode("utf-8")
    headers = {"Authorization": f"Bearer {admin_refresh_token}"}
    print(f"DEBUG {admin_refresh_token}")

    response = await client.get("/users/list", headers=headers)
    assert response.status_code == 401
    assert response.json()["error_code"] == "INVALID_TOKEN_TYPE"

    # Regular user without administrative privileges
    user_token = create_access_token({"sub": "Darth Vader"}).decode("utf-8")
    headers_user = {"Authorization": f"Bearer {user_token}"}

    response_user = await client.get("/users/list", headers=headers_user)
    assert response_user.status_code == 403
    assert response_user.json()["error_code"] == "FORBIDDEN"


async def test_delete_user_access_control(client, async_session):
    """
    Testing endpoint access control (admin only).
    Endpoint DELETE /users/{user_id}.
    """
    await add_users(async_session)

    # Admin (Aragorn II)
    admin_token = create_access_token({"sub": "Aragorn II"}).decode("utf-8")
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    existing_user_id = 15

    response_admin = await client.delete(
        f"/users/{existing_user_id}", headers=headers_admin
    )

    assert response_admin.status_code == 200
    assert "deleted successfully" in response_admin.json()["message"]

    # Check the db
    query = select(User).where(User.id == existing_user_id)
    result = await async_session.execute(query)
    deleted_user = result.scalars().first()

    assert deleted_user is None

    non_existing_user_id = 999

    response_admin = await client.delete(
        f"/users/{non_existing_user_id}", headers=headers_admin
    )

    assert response_admin.status_code == 404
    assert response_admin.json()["error_code"] == "NOT_FOUND"

    # Regular user without administrative privileges
    user_token = create_access_token({"sub": "Darth Vader"}).decode("utf-8")
    headers_user = {"Authorization": f"Bearer {user_token}"}

    response_user = await client.delete(
        f"/users/{existing_user_id}", headers=headers_user
    )

    assert response_user.status_code == 403
    assert response_user.json()["error_code"] == "FORBIDDEN"


async def test_user_info(client, async_session):
    """
    Testing endpoint for getting the current user info.
    Endpoint GET /users/user_info.
    """
    await add_users(async_session)
    payload = {"username": "Hermione G.", "password": "Str0ngP@ssword"}

    access_token = create_access_token({"sub": payload["username"]}).decode("utf-8")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.get("/users/user_info", headers=headers)

    assert response.status_code == 200
    assert response.json()["username"] == payload["username"]

    # Non-existing user
    access_token = create_access_token({"sub": "Carrie Bradhsaw"}).decode("utf-8")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.get("/users/user_info", headers=headers)

    assert response.status_code == 404
    assert response.json()["message"] == "User not found"
