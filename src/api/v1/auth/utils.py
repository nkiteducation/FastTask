import uuid

from datetime import datetime, timedelta, timezone

import jwt

from passlib.context import CryptContext

from core.settings import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_PRIVATE_KEY = config.jwt.private_key_path.read_text()
_PUBLIC_KEY = config.jwt.public_key_path.read_text()
_ALGORITHM = config.jwt.algorithm
_ISSUER = config.project.name
_AUDIENCE = "my-api"


def password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def encode_jwt(payload: dict, expire_delta: timedelta = timedelta(minutes=15)) -> str:
    now = datetime.now(timezone.utc)
    to_encode = {
        **payload,
        "iat": now,
        "exp": now + expire_delta,
        "iss": _ISSUER,
        "aud": _AUDIENCE,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(to_encode, key=_PRIVATE_KEY, algorithm=_ALGORITHM)


def decode_jwt(token: str) -> dict:
    return jwt.decode(
        jwt=token,
        key=_PUBLIC_KEY,
        algorithms=[_ALGORITHM],
        audience=_AUDIENCE,
        issuer=_ISSUER,
    )
