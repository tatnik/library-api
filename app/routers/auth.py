from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.database import SessionLocal
from app import models, schemas, utils
from app.core.config import settings


router = APIRouter(tags=["Auth"])

      
@router.post("/register", response_model=schemas.UserRead)
def register(user_in: schemas.UserCreate, db: Session = Depends(utils.get_db)):
    # проверка существования пользователя
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed = utils.get_password_hash(user_in.password)
    new_user = models.User(email=user_in.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(utils.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password",
                            headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return schemas.Token(access_token=access_token, token_type="bearer")

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(token: str = Depends(utils.oauth2_scheme)):
    """Logout endpoint. Отзывает токен и добавляет его в черный список."""
    utils.revoke_token(token)
    return

@router.get("/me", response_model=schemas.UserRead)
def read_users_me(current_user: models.User = Depends(utils.get_current_user)):
    """Информация о текущем пользователе"""
    return current_user
