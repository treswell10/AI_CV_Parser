from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)  # matches the bcrypt 72-byte limit


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # lets Pydantic read SQLAlchemy objects


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"