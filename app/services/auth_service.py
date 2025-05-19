from datetime import timedelta
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, Token
from app.core.config import settings
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, get_current_user as security_get_current_user,
    oauth2_scheme, revoke_token as security_revoke_token
)


oauth2_scheme = oauth2_scheme


class AuthService:
    """
    Service for user registration, authentication and JWT handling.
    """
    oauth2_scheme = oauth2_scheme

    @staticmethod
    def user_exists(db: Session, email: str) -> bool:
        """Check if user with given email exists."""
        return db.query(User).filter(User.email == email).first() is not None

    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        """Create and store a new user with a hashed password."""
        hashed_password = get_password_hash(user_in.password)
        user = User(email=user_in.email, hashed_password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Validate email and password, return user on success or None."""
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Generate a JWT access token."""
        return create_access_token(data=data, expires_delta=expires_delta)

    @classmethod
    def get_current_user(cls,
                         token: str = Depends(oauth2_scheme),
                         db: Session = Depends(get_db)
                         ) -> User:
        """Delegate token decoding and user lookup to security module."""
        return security_get_current_user(token=token, db=db)

    @staticmethod
    def revoke_token(token: str) -> None:
        """Delegate token revocation to security module."""
        security_revoke_token(token)
