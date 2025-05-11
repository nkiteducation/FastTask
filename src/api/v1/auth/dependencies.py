from typing import Annotated

from fastapi import Form
from pydantic import EmailStr, SecretStr

from api.v1.shemas import UserCreate


def get_form_user(
    name: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    password: Annotated[SecretStr, Form()],
):
    return UserCreate(name=name, email=email, password=password)
