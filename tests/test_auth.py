from sqlalchemy import select

from freezegun import freeze_time

from app.database.models import User, RevokedToken
from tests.conftest import client, async_session
from tests.utils import add_users

import jwt
from app.core.security import (
    SECRET_KEY,
    ALGORITHM,
    create_access_token,
    create_refresh_token,
)


async def test_create_user_success(client, async_session):
    """
    Successful user creation test.
    Endpoint POST /auth/register.
    """
    payload = {"username": "Carrie Bradhsaw", "password": "Il0veM@ano1o"}

    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()

    assert "successfully registered" in data["message"]

    # Check the database
    query = select(User).where(User.username == payload["username"])
    result = await async_session.execute(query)
    new_user_db = result.scalars().first()

    assert new_user_db.id is not None
    assert new_user_db.is_admin is False
    assert new_user_db.hashed_password != payload["password"]


async def test_create_user_duplicate(client, async_session):
    """
    Error 409: creating a user with an existing username.
    Endpoint POST /auth/register.
    """
    payload = {"username": "Darth Vader", "password": "Wing@rdium1evi0&a"}

    await add_users(async_session)

    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 409
    assert response.json()["error_code"] == "CONFLICT"


async def test_login_success(client, async_session):
    """
    Successful login with token pair generation.
    Endpoint POST /auth/login.
    """
    payload = {"username": "Hermione G.", "password": "Str0ngP@ssword"}

    await add_users(async_session)

    response = await client.post("/auth/login", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["sub"] == payload["username"]

    decode_payload = jwt.decode(
        data["refresh_token"], SECRET_KEY, algorithms=[ALGORITHM]
    )

    assert decode_payload["sub"] == payload["username"]
    assert "exp" in decode_payload


async def test_login_fail(client, async_session):
    """
    Error 404, 409.
    Endpoint POST /auth/login.
    """
    await add_users(async_session)

    payload = {"username": "Hermione Granger", "password": "Str0ngP@ssword"}

    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 404
    assert response.json()["error_code"] == "NOT_FOUND"

    payload = {"username": "Hermione G.", "password": "Str0ngP@sswor"}

    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["error_code"] == "INVALID_CREDENTIALS"


async def test_logout_success(client, async_session):
    """
    Successful logout with the revoked token added to the db.
    Endpoint POST /auth/logout.
    """
    payload = {"username": "Hermione G.", "password": "Str0ngP@ssword"}
    await add_users(async_session)

    refresh_token = create_refresh_token({"sub": payload["username"]})

    headers = {"x-refresh-token": refresh_token}
    logout_response = await client.post("/auth/logout", headers=headers)

    assert logout_response.status_code == 200
    assert "Logged out" in logout_response.json()["message"]

    # Is revoked? Check the db
    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    expire_timestamp = payload.get("exp")  # Unix format

    jti = payload["jti"]

    query = select(RevokedToken).where(RevokedToken.jti == jti)
    result = await async_session.execute(query)
    revoked_token = result.scalars().first()

    expires_at_unix = revoked_token.expires_at.timestamp()

    assert revoked_token is not None
    assert expires_at_unix == expire_timestamp


async def test_logout_invalid_token(client, async_session):
    """
    Error 401: attempt to log out with an invalid token + Empty headers
    Endpoint POST /auth/logout.
    """
    payload = {"username": "Hermione G.", "password": "Str0ngP@ssword"}
    await add_users(async_session)

    refresh_token = create_refresh_token({"sub": payload["username"]})
    refresh_token_garbaged = refresh_token + "garbage".encode("utf-8")

    headers = {"x-refresh-token": refresh_token_garbaged}
    logout_response = await client.post("/auth/logout", headers=headers)

    assert logout_response.status_code == 401
    assert logout_response.json()["error_code"] == "INVALID_TOKEN"

    logout_response = await client.post("/auth/logout")

    assert logout_response.status_code == 400
    assert "Field: ('header', 'x-refresh-token')" in logout_response.text


async def test_refresh_token_success(client, async_session):
    """
    Successful tokens update. Checking whether the old refresh token
    has been added to the db, and the ability to refresh tokens using it.
    Endpoint POST /auth/refresh.
    """
    payload = {"username": "Hermione G.", "password": "Str0ngP@ssword"}
    await add_users(async_session)

    with freeze_time("2026-01-17 12:00:00"):
        login_response = await client.post("/auth/login", json=payload)
        old_tokens = login_response.json()

        old_refresh_token = old_tokens["refresh_token"]
        old_payload = jwt.decode(old_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        old_jti = old_payload["jti"]  # Old data to compare

    with freeze_time("2026-01-17 12:00:05"):
        headers = {"x-refresh-token": old_refresh_token}
        refresh_response = await client.post("/auth/refresh", headers=headers)

        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()

        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens

        assert new_tokens["access_token"] != old_tokens["access_token"]
        assert new_tokens["refresh_token"] != old_tokens["refresh_token"]

        # Check the db
        query = select(RevokedToken).where(RevokedToken.jti == old_jti)
        result = await async_session.execute(query)
        revoked_token = result.scalars().first()

        assert revoked_token is not None

        # Attempt to refresh with the revoked token
        retry = await client.post("/auth/refresh", headers=headers)
        assert retry.status_code == 401
        assert retry.json()["error_code"] == "TOKEN_REVOKED"


async def test_refresh_token_fail(client, async_session):
    """
    Error 401: attempt to refresh tokens with an invalid token, invalid token type.
    Endpoint POST /auth/refresh.
    """
    payload = {"username": "Hermione G.", "password": "Str0ngP@ssword"}
    await add_users(async_session)

    refresh_token = create_refresh_token({"sub": payload["username"]})
    refresh_token_garbaged = refresh_token + "garbage".encode("utf-8")

    headers = {"x-refresh-token": refresh_token_garbaged}
    response = await client.post("/auth/refresh", headers=headers)

    assert response.status_code == 401
    assert response.json()["error_code"] == "INVALID_TOKEN"

    # Access token
    access_token = create_access_token({"sub": payload["username"]})

    headers = {"x-refresh-token": access_token}
    response = await client.post("/auth/refresh", headers=headers)

    assert response.status_code == 401
    assert response.json()["error_code"] == "INVALID_TOKEN_TYPE"

    # Empty headers
    response = await client.post("/auth/refresh")

    assert response.status_code == 400
    assert "Field: ('header', 'x-refresh-token')" in response.text
