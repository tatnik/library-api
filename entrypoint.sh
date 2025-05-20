#!/usr/bin/env bash
set -e

echo "⏳ Ждём, пока станет доступна БД..."
until pg_isready -h db -U "$POSTGRES_USER"; do
  sleep 1
done

echo "🚀 Применяем  миграции..."
alembic upgrade head

echo "🎉 Запускаем API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
