from fastapi import FastAPI
from app.database import engine, Base

# Упрощённый main для миграций Alembic
# Не создаём таблицы и не подключаем роутеры, чтобы избежать ошибок при запуске внутри контейнера

app = FastAPI()
