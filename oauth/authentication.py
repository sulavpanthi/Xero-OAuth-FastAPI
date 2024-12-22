from datetime import UTC, datetime, timedelta
from typing import Literal

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from passlib.context import CryptContext

from core.config import config

AUTHENTICATION_EXCEPTION = HTTPException(
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

REFRESH_TOKEN_EXCEPTION = HTTPException(
    status_code=400,
    detail="Could not validate refresh token",
)

SECRET_KEY = config.secret_key
REFRESH_SECRET_KEY = config.refresh_secret_key
ALGORITHM = config.algorithm

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()


def create_jwt_token(
    data: dict, expires_delta: timedelta | None = None, token_type="access"
):
    to_encode = data.copy()
    if not expires_delta:
        if token_type == "access":
            expires_delta = timedelta(minutes=config.access_token_expiry_minutes)
        else:
            expires_delta = timedelta(minutes=config.refresh_token_expiry_minutes)

    secret = REFRESH_SECRET_KEY if token_type == "refresh" else SECRET_KEY
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire, "iat": datetime.now(UTC)})
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str, token_type: Literal["access", "refresh"] = "access"):
    if not token:
        return None, []
    scopes = []
    try:
        secret = REFRESH_SECRET_KEY if token_type == "refresh" else SECRET_KEY
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("uid")
        scopes = payload.get("scopes", [])
        if user_id is None:
            raise AUTHENTICATION_EXCEPTION
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        if token_type == "refresh":
            raise REFRESH_TOKEN_EXCEPTION
        else:
            raise AUTHENTICATION_EXCEPTION
    return payload, scopes


def get_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    payload, _ = decode_token(credentials.credentials)
    return payload.get("uid")
