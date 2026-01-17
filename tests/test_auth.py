from freezegun import freeze_time
from fastapi.testclient import TestClient
from app.main import app
from app.models.models import User, RevokedToken
from tests.conftest import db_session
from tests.utils import add_users

import jwt
from app.dependencies.security import (
    SECRET_KEY,
    ALGORITHM,
    create_access_token,
    create_refresh_token,
)

client = TestClient(app)


def test_create_user_success(client, db_session):
    """
    Successful user creation test.
    Endpoint POST /auth/register.
    """
    payload = {"username": "Carrie Bradhsaw", "password": "Il0veM@ano1o"}

    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()

    assert "successfully registered" in data["message"]

    new_user_db = db_session.query(User).filter_by(username=payload["username"]).first()

    assert new_user_db.id is not None
    assert new_user_db.is_admin is False

    assert new_user_db.username == payload["username"]
    assert new_user_db.hashed_password != payload["password"]


def test_create_user_duplicate(client, db_session):
    """
    Error 409: creating a user with an existing username.
    Endpoint POST /auth/register.
    """
    payload = {"username": "Darth Vader", "password": "Wing@rdium1evi0&a"}

    add_users(db_session)

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 409
    assert response.json()["error_code"] == "CONFLICT"


def test_login_success(client, db_session):
    """
    Successful login with token pair generation.
    Endpoint POST /auth/login.
    """
    payload = {"username": "Hermione G.", "password": "Str0ngP@ssword"}
    add_users(db_session)

    response = client.post("/auth/login", json=payload)

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


def test_login_not_found(client, db_session):
    """
    Error 404: the user with this username not found.
    Endpoint POST /auth/login.
    """
    payload = {"username": "Hermione Granger", "password": "Str0ngP@ssword"}

    add_users(db_session)

    response = client.post("/auth/login", json=payload)
    assert response.status_code == 404
    assert response.json()["error_code"] == "NOT FOUND"


def test_login_invalid_credentials(client, db_session):
    """
    Error 401: the user entered incorrect password.
    Endpoint POST /auth/login.
    """
    payload = {"username": "Hermione G.", "password": "Str0ngP@sswor"}

    add_users(db_session)

    response = client.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["error_code"] == "UNAUTHORIZED"


def test_logout_success(client, db_session):
    """
    Successful logout with the revoked token added to the db.
    Endpoint POST /auth/logout.
    """
    payload = {"username": "Hermione G.", "password": "Str0ngP@ssword"}
    add_users(db_session)

    login_response = client.post("/auth/login", json=payload)
    refresh_token = login_response.json()["refresh_token"]

    headers = {"x-refresh-token": refresh_token}
    logout_response = client.post("/auth/logout", headers=headers)

    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Logged out successfully"

    # Is revoked?
    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    expire_timestamp = payload.get("exp")  # Unix format

    jti = payload["jti"]

    revoked_token = db_session.query(RevokedToken).filter_by(jti=jti).first()

    expires_at_unix = revoked_token.expires_at.timestamp()

    assert revoked_token is not None
    assert revoked_token.jti == jti
    assert expires_at_unix == expire_timestamp


def test_logout_invalid_token(client, db_session):
    """
    Error 401: attempt to log out with an invalid token.
    Endpoint POST /auth/logout.
    """
    payload = {"username": "Hermione G.", "password": "Str0ngP@ssword"}
    add_users(db_session)

    login_response = client.post("/auth/login", json=payload)
    refresh_token = login_response.json()["refresh_token"] + "garbage"

    headers = {"x-refresh-token": refresh_token}
    logout_response = client.post("/auth/logout", headers=headers)

    assert logout_response.status_code == 401
    assert logout_response.json()["error_code"] == "INVALID_TOKEN"


def test_refresh_token_success(client, db_session):
    """
    Successful tokens update. Checking whether the old refresh token
    has been added to the db, and the ability to refresh tokens using it.
    Endpoint POST /auth/refresh.
    """
    payload = {"username": "Hermione G.", "password": "Str0ngP@ssword"}
    add_users(db_session)

    with freeze_time("2026-01-17 12:00:00"):
        login_response = client.post("/auth/login", json=payload)
        old_tokens = login_response.json()

    old_refresh_token = old_tokens["refresh_token"]
    old_payload = jwt.decode(old_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    old_jti = old_payload["jti"]  # Old data to compare

    with freeze_time("2026-01-17 12:00:05"):
        headers = {"x-refresh-token": old_refresh_token}
        refresh_response = client.post("/auth/refresh", headers=headers)

    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()

    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens

    assert new_tokens["access_token"] != old_tokens["access_token"]
    assert new_tokens["refresh_token"] != old_tokens["refresh_token"]

    # Is revoked?
    revoked = db_session.query(RevokedToken).filter_by(jti=old_jti).first()
    assert revoked is not None

    # Attempt to refresh with the revoked token
    retry = client.post("/auth/refresh", headers=headers)
    assert retry.status_code == 401
    assert retry.json()["error_code"] == "TOKEN_REVOKED"


def test_refresh_token_invalid(client, db_session):
    """
    Error 401: attempt to refresh tokens with an invalid token.
    Endpoint POST /auth/refresh.
    """
    payload = {"username": "Hermione G.", "password": "Str0ngP@ssword"}
    add_users(db_session)

    login_response = client.post("/auth/login", json=payload)
    refresh_token = login_response.json()["refresh_token"] + "garbage"

    headers = {"x-refresh-token": refresh_token}
    response = client.post("/auth/refresh", headers=headers)

    assert response.status_code == 401
    assert response.json()["error_code"] == "INVALID_TOKEN"


def test_refresh_token_invalid_type(client, db_session):
    """
    Error 401: attempt to refresh tokens with an invalid token type.
    Endpoint POST /auth/refresh.
    """
    payload = {"username": "Hermione G.", "password": "Str0ngP@ssword"}
    add_users(db_session)

    login_response = client.post("/auth/login", json=payload)
    access_token = login_response.json()["access_token"]

    headers = {"x-refresh-token": access_token}
    response = client.post("/auth/refresh", headers=headers)

    assert response.status_code == 401
    assert response.json()["error_code"] == "INVALID_TOKEN_TYPE"


def test_get_users_access_control(client, db_session):
    """
    Testing endpoint access control (admin only).
    Endpoint GET /auth/users.
    """
    add_users(db_session)

    # Admin (Aragorn II)
    admin_token = create_access_token({"sub": "Aragorn II"})
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    response_admin = client.get("/auth/users", headers=headers_admin)
    assert response_admin.status_code == 200
    assert len(response_admin.json()) == 3

    # Refresh token
    admin_refresh_token = create_refresh_token({"sub": "Aragorn II"})
    headers = {"Authorization": f"Bearer {admin_refresh_token}"}

    response = client.get("/auth/users", headers=headers)
    assert response.status_code == 401
    assert response.json()["error_code"] == "INVALID_TOKEN_TYPE"

    # User
    user_token = create_access_token({"sub": "Darth Vader"})
    headers_user = {"Authorization": f"Bearer {user_token}"}

    response_user = client.get("/auth/users", headers=headers_user)
    assert response_user.status_code == 403
    assert response_user.json()["error_code"] == "FORBIDDEN"
