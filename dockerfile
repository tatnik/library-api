FROM python:3.9-slim

WORKDIR /code

# 1) Устанавливаем системные зависимости для pg_isready
RUN apt-get update \
    && apt-get install -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 2) Устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Копируем весь проект 
COPY . .

# 4) Копируем etrypoint.sh (без этой команды Ubunta его не находит)
COPY entrypoint.sh /entrypoint.sh

# 5) Делаем скрипт исполняемым
RUN chmod +x /entrypoint.sh

# 6) Запускаемся через entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
