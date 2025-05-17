from fastapi import FastAPI
from app.database import engine, Base
from app.core.config import settings
from app.routers.auth import router as auth_router # импортируем роутеры


app = FastAPI(
    title="Library API",
    description="RESTful API для управления библиотечным каталогом",
    version="1.0.0"
)


app.include_router(auth_router, prefix="/auth", tags=["Auth"])
