from datetime import datetime, timedelta
from typing import Optional, Set
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException,Security, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import get_db
from app.models.user import User

# --- Constants and dependencies ---
api_key_scheme = APIKeyHeader(name="Authorization", auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
revoked_tokens: Set[str] = set()

def get_token(api_key: str = Security(api_key_scheme)):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No auth token"
        )
    if api_key.startswith("Bearer "):
        return api_key[len("Bearer "):]
    return api_key

def get_password_hash(password: str) -> str:
    """Return bcrypt hash of the given password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a JWT with subject and expiry."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    """Decode and verify JWT, returning its payload."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise credentials_exception


def get_current_user(
    token: str = Depends(get_token),
    db: Session = Depends(get_db)
) -> User:
    """Return current authenticated user or raise credentials exception."""
    if token in revoked_tokens:
        raise credentials_exception
    payload = decode_access_token(token)
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


def revoke_token(token: str) -> None:
    """Add token to in-memory blacklist."""
    revoked_tokens.add(token)
