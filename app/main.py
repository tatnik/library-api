from fastapi import FastAPI
from app.db import engine, Base
from app.core.config import settings
from app.routers.auth import router as auth_router 
from app.routers.books import router as books_router
from app.routers.readers import router as readers_router
from app.routers.loan import router as loan_router


app = FastAPI(
    title="Library API",
    description="RESTful API для управления библиотечным каталогом",
    version="1.0.0"
)


app.include_router(auth_router)
app.include_router(books_router)
app.include_router(readers_router)
app.include_router(loan_router)  
