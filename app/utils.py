from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import SessionLocal
from app.models import User

from typing import Set

# Создаём контекст шифрования для bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme для получения токена из запроса
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Общий exception для неверных токенов
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# Хранилище отозванных токенов (in-memory blacklist)
revoked_tokens: Set[str] = set()

# Сессия БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Хеширование пароля
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Проверка пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Создание JWT-токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


# Получение текущего пользователя из токена
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    if token in revoked_tokens:
        raise credentials_exception
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def revoke_token(token: str) -> None:
    """
    Помечает токен отозванным, добавляя в blacklist.
    """
    revoked_tokens.add(token)
