FROM python:3.9-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# При старте выполняем миграции и запускаем Uvicorn
ENTRYPOINT ["bash", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --reload"]
