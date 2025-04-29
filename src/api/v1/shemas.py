from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr


class BaseUser(BaseModel):
    name: str
    email: EmailStr


class UserInput(BaseUser):
    password: SecretStr


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[SecretStr] = None


class UserReturn(BaseUser):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
