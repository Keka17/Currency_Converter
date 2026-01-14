from pydantic import BaseModel, ConfigDict, field_validator
import re


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


class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str
    password: str
