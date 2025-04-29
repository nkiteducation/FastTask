from datetime import UTC, datetime, timedelta
from pathlib import Path

import jwt

from passlib.context import CryptContext

from core.settings import config

pwd_context = CryptContext(schemes=["bcrypt"])


def encode_jwt(
    payload: dict,
    private_key: str = config.jwt.private_key_path.read_text(),
    algorithm: Path = config.jwt.algorithm,
    expire_minutes: timedelta = timedelta(minutes=15),
):
    to_encode = payload.copy()
    to_encode.update(iat=datetime.now(UTC), exp=datetime.now(UTC) + expire_minutes)
    return jwt.encode(payload=to_encode, key=private_key, algorithm=algorithm)


def decode_jwt(
    encoded_jwt: str | bytes,
    public_key: str = config.jwt.public_key_path.read_text(),
    algorithm: Path = config.jwt.algorithm,
):
    return jwt.decode(jwt=encoded_jwt, key=public_key, algorithms=[algorithm])


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)
