# Library API

**RESTful API для управления библиотечным каталогом**

---

## 🎯 Быстрый старт

1. **Клонирование репозитория**
   ```bash
   git clone https://github.com/tatnik/library-api
   cd library-api
   ```

2. **Создание `.env` в корне проекта**
   ```dotenv
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=library_db
   DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/library_db
   SECRET_KEY=your_super_secret_key
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. **Создание папок для данных**
   ```bash
   mkdir -p data/postgres
   mkdir -p data/tests
   ```

4. **Запуск через Docker Compose**
   ```bash
   docker-compose up -d --build
   ```

5. **Первичная регистрация пользователя**
   - Откройте [http://localhost:8000/docs](http://localhost:8000/docs)
   - В разделе **Auth** выполните `POST /auth/register` с телом:
     ```json
     {"email": "admin@example.com", "password": "strongpass"}
     ```
   - Затем выполните `POST /auth/login` (form-data) и получите `access_token`.

---

## 📁 Структура проекта

```
library-api/
├── .env
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── README.md
├── requirements.txt
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── app/
│   ├── main.py          # точка входа FastAPI
│   ├── db.py            # SQLAlchemy engine, Session, Base, get_db
│   ├── models.py        # ORM-модели: User, Book, Reader, BorrowedBook
│   ├── schemas.py       # Pydantic-схемы
│   ├── security.py      # JWT, пароли, зависимости
│   ├── core/config.py   # Pydantic Settings
│   └── routers/
│       ├── auth.py      # регистрация, логин, logout, me
│       ├── books.py     # CRUD книг и публичные GET
│       ├── readers.py   # CRUD читателей
│       └── borrow.py    # выдача/возврат книг, список невозвращённых
├── data/
│   ├── postgres
│   └── tests
└── tests/
    ├── test_auth.py
    ├── test_books.py
    ├── test_borrow.py
    ├── test_db_schema.py
    └── test_readers.py
```

---

## 🗄️ Структура базы данных

- **users**: библиотекари (`email`, `hashed_password`, `is_active`)
- **books**: книги (`title`, `author`, `published_year`, `isbn`, `copies`, `description`)
- **readers**: читатели (`name`, `email`, `phone`)
- **borrowed_books**: история выдач (`book_id`, `reader_id`, `loan_date`, `return_date`)
- **alembic_version**: служебная таблица миграций

**Особенности:**
- Отдельная таблица `loans` для ограничения и истории выдач.
- Индексы по `id`, `email`, `isbn` для быстрого поиска.

---

## 🚀 Примеры использования API

### 1. Регистрация пользователя (библиотекаря)

```bash
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d '{"email": "admin@example.com", "password": "StrongPassword123"}'
```

**Ответ (201 Created):**
```json
{
  "id": 1,
  "email": "admin@example.com"
}
```

---

### 2. Получение access token (логин)

```bash
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin@example.com&password=StrongPassword123"
```

**Ответ (200 OK):**
```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer"
}
```

---

### 3. Создание книги (POST /books/) — требуется авторизация

```bash
curl -X POST http://localhost:8000/books/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{"title": "Мастер и Маргарита", "author": "М. Булгаков", "published_year": 1967, "isbn": "123-4567890123", "copies": 5, "description": "Классика"}'
```

**Ответ (201 Created):**
```json
{
  "id": 1,
  "title": "Мастер и Маргарита",
  "author": "М. Булгаков",
  "published_year": 1967,
  "isbn": "123-4567890123",
  "copies": 5,
  "description": "Классика"
}
```

---

### 4. Получить список всех книг (GET /books/)

```bash
curl http://localhost:8000/books/
```

**Ответ (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Мастер и Маргарита",
    "author": "М. Булгаков",
    "published_year": 1967,
    "isbn": "123-4567890123",
    "copies": 5,
    "description": "Классика"
  }
]
```

---

### 5. Выдача книги читателю (POST /loans/) — требуется авторизация

```bash
curl -X POST http://localhost:8000/loans/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{"book_id": 1, "reader_id": 2}'
```

**Ответ (201 Created):**
```json
{
  "id": 1,
  "book_id": 1,
  "reader_id": 2,
  "loan_date": "2024-05-21T10:00:00",
  "return_date": null
}
```

---

### 6. Возврат книги (POST /loans/return) — требуется авторизация

```bash
curl -X POST http://localhost:8000/loans/return \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{"book_id": 1, "reader_id": 2}'
```

**Ответ (200 OK):**
```json
{
  "id": 1,
  "book_id": 1,
  "reader_id": 2,
  "loan_date": "2024-05-21T10:00:00",
  "return_date": "2024-05-22T13:45:00"
}
```

## ⚙️ Бизнес-логика

1. **Выдача книги** (`POST /borrow/`)
   - Проверяется наличие экземпляров (`copies > 0`), иначе — `400 Bad Request`.
   - При выдаче `copies` уменьшается на 1, создаётся запись в `borrowed_books` с `return_date = NULL`.

2. **Ограничение выдачи**
   - Один читатель может иметь не более **3** невозвращённых книг одновременно.

3. **Возврат книги** (`POST /return/`)
   - Ищется активная выдача (`return_date IS NULL`), иначе — `400 Bad Request`.
   - `return_date` обновляется, в `books` увеличивается `copies`.

**Особое внимание:**  
- Все операции — транзакционные, чтобы избежать рассинхронизации по количеству книг.
- Проверка лимитов выдачи реализована на уровне запроса к `borrowed_books`.

---

## 🔒 Аутентификация

- Используется **JWT** (`python-jose[cryptography]`)
- Пароли хешируются через `passlib[bcrypt]`
- Защищённые эндпоинты:
  - CRUD по книгам и читателям
  - выдача/возврат книг
- Публичные:
  - Получение списка и деталей книг (`GET /books/`, `GET /books/{id}`)

---

## 💡 Резервирование книг (дополнительная фича)

**Описание:**
- Позволяет резервировать книгу, если все экземпляры заняты.
- Настраиваемый срок хранения резерва (`RESERVATION_RESERVED_DAYS` в конфиге).
- Таблица `reservations` хранит заявки на резерв, даты уведомлений, статусы (`PENDING`, `RESERVED`, `NOTIFIED`, `COMPLETED`, `CANCELLED`, `EXPIRED`).
- Поток работы: создание заявки — возврат книги — резервирование — уведомление — выдача или отмена.
- Периодическая задача (Celery/APScheduler) снимает истёкшие резервы и очищает старые записи.

**API:**
- `POST /reservations/` — добавить резерв
- `GET /reservations/{id}` — детали резерва по ID
- `GET /reservations?reader_id={reader_id}` — список резервов по читателю
- `GET /reservations?book_id={book_id}` — список резервов по книге
- `GET /reservations?reader_id=1&status=RESERVED` - фильтрация по нескольким полям
- `PATCH /reservations/notifyall/` — отправить уведомления всем ожидающим
- `PATCH /reservations/{id}/complete` — оформить выдачу
- `PATCH /reservations/{id}/cancel` — отменить резерв

---

## 🧪 Тестирование и стратегия покрытия

### Как устроено тестирование

- Используется **pytest** + FastAPI TestClient.
- Каждый тест изолирован, создаётся уникальная тестовая база.
- Все данные в тестах уникальны, фикстуры генерируют новых пользователей и токены.
- Миграции и структура схемы проверяются отдельно (`test_db_schema.py`).

### Почему так

- **Изоляция** — гарантирует независимость тестов.
- **Нет “магических” данных** — всё создаётся явно.
- **Легко поддерживать** и расширять.

### Как запустить тесты

```bash
pip install -r requirements.txt
pytest -v
pytest --cov=app tests/
```
> _Изоляция замедляет тесты, но обеспечивает 100% стабильность._

### Стратегия покрытия

- Покрываются не только “счастливые” сценарии, но и все бизнес-ограничения (лимиты, ошибки, повторные возвраты).
- Покрытие бизнес-логики — 90%+ (см. отчёт о coverage).

---
