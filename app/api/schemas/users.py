from pydantic import BaseModel, ConfigDict, field_validator
import re


def example_user_out(schema: dict) -> None:
    schema["example"] = {"username": "Darth Vader", "id": 66, "is_admin": True}


def example_user_in(schema: dict) -> None:
    schema["example"] = {"username": "Darth Vader", "password": "Str0ngP@$$w678"}


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    def validate_password(cls, password) -> str:
        pattern = (
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$"
        )

        if re.fullmatch(pattern, password):
            return password
        else:
            raise ValueError(
                "Weak password! Recommendations for a strong password: "
                "minimum length - 12 characters, upper and lower case letters, "
                "at least one number and  special characters (@$!%*?&)"
            )

    model_config = ConfigDict(json_schema_extra=example_user_in)


class User(UserBase):
    id: int
    is_admin: bool

    model_config = ConfigDict(from_attributes=True, json_schema_extra=example_user_out)


class UserLogin(BaseModel):
    username: str
    password: str
