from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.schemas.auth import UserCreate, UserRead, Token
from app.services.auth_service import AuthService
from app.db import get_db
from app.core.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new librarian"
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Создаёт нового пользователя (библиотекаря) с хешированным паролем.
    """
    if AuthService.user_exists(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    user = AuthService.create_user(db, user_in)
    return user

@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate and receive access token"
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Проверяет email и пароль, возвращает JWT.
    """
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = AuthService.create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(access_token=access_token, token_type="bearer")

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke current access token"
)
def logout(
    token: str = Depends(AuthService.oauth2_scheme)
):
    """
    Отзывает текущий токен, добавляя его в черный список.
    """
    AuthService.revoke_token(token)

@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user"
)
def read_current_user(
    current_user: UserRead = Depends(AuthService.get_current_user)
):
    """
    Возвращает информацию о текущем аутентифицированном пользователе.
    """
    return current_user
