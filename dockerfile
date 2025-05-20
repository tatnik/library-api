FROM python:3.9-slim

WORKDIR /code

# 1) Устанавливаем системные зависимости для pg_isready
RUN apt-get update \
    && apt-get install -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 2) Устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Копируем весь проект (включая entrypoint.sh) и делаем скрипт исполняемым
COPY . .
RUN chmod +x ./entrypoint.sh

# 4) Запуск через entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
