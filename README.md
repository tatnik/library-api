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

3. **Создание папки для базы данных**
   ```bash
   mkdir -p data/postgres
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
│   ├── core/
│   │   ├── config.py    # Pydantic Settings
│   │   └── securiti.py  # JWT, пароли, зависимости   
│   ├── models/          # ORM-модели
│   │   ├── mixins.py      
│   │   ├── book.py     
│   │   ├── loan.py     
│   │   ├── reader.py   
│   │   └── user.py    
│   ├── routers/
│   │   ├── auth.py      # регистрация, логин, logout, me
│   │   ├── book.py      # CRUD книг и публичные GET
│   │   ├── reader.py    # CRUD читателей
│   │   └── loan.py      # выдача/возврат книг, список невозвращённых
│   ├── shemas/          # Pydantic-схемы 
│   │   ├── auth.py      
│   │   ├── book.py     
│   │   ├── loan.py       
│   │   └── reader.py    
│   └── services/
│       ├── auth_service.py      
│       ├── book_service.py     
│       ├── loan_service.py       
│       └── reader_service.py    
├── data/
│   └── postgres         # База данных   
└── tests/
    ├── conftest.py
    ├── test_auth.py
    ├── test_book.py
    ├── test_loan.py
    ├── test_db_schema.py
    └── test_reader.py
```

---

## 🗄️ Структура базы данных

- **users**: библиотекари (`email`, `hashed_password`, `is_active`)
- **books**: книги (`title`, `author`, `published_year`, `isbn`, `copies`, `description`)
- **readers**: читатели (`name`, `email`, `phone`)
- **loans**: история выдач (`book_id`, `reader_id`, `loan_date`, `return_date`)
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

1. **Выдача книги** (`POST /loans/`)

   * Проверяем, что книга есть в наличии (в таблице **books** для выбранной книги `copies > 0`). Если книги в наличии нет,  возвращаем — `400 Bad Request`.
   * Уменьшаем copies на 1 и создаём запись в **loans** с `return_date = NULL`.

2. **Ограничение выдачи**

   - Один читатель может иметь не более **3** невозвращённых книг одновременно.
    (считаем  количество записей в таблице **loans**  по `reader_id`, для которых `return_date IS NULL`).


3. **Возврат книги** (`POST /loans/return/`)

   * В таблице **loans** ищем запись с `book_id`, `reader_id` и `return_date IS NULL`.
   * Если не найдена — `400 Bad Request`.
   * Устанавливаем `return_date = now()`,
   * В таблице **books** для записи с `id = book_id` увеличиваем copies на 1.

---

## 🔒 Аутентификация

- Для защиты операций используется **JWT** (JSON Web Token) через библиотеку [`python-jose[cryptography]`](https://python-jose.readthedocs.io/en/latest/):
  - **Почему JWT?** Позволяет быстро и удобно реализовать stateless-аутентификацию, хорошо подходит для SPA и мобильных клиентов, легко интегрируется с FastAPI.
  - **Почему python-jose?** Это одна из самых популярных и поддерживаемых библиотек для работы с JWT в Python, обеспечивает высокую безопасность и гибкость настройки алгоритмов подписи.
- Хеширование паролей выполняется через [`passlib[bcrypt]`](https://passlib.readthedocs.io/en/stable/):
  - **Почему passlib + bcrypt?** Bcrypt — промышленный стандарт, надёжно защищает пароли от атак по словарю и перебору. Passlib — удобная обёртка, устойчивая к ошибкам настройки.

**Способы доступа к эндпоинтам:**

- **Защищённые эндпоинты (требуется JWT):**
  - Операции создания, обновления и удаления книг и читателей (**CRUD**)
  - Операции выдачи и возврата книг, а также получение списков взятых книг у читателя.
  - Получение и изменение информации о пользователе (`/auth/me`, `/auth/logout` и т.д.)
- **Публичные эндпоинты:**
  - Получение списка книг и информации о книге (`GET /books/`, `GET /books/{id}`)
  
   Каталог открыт для просмотра — это удобно для потенциальных читателей, клиентов или интеграции с внешними сервисами.

**Обоснование разбивки на публичные и защищённые эндпоинты:**
- **Все операции, которые могут изменить состояние системы, требуют аутентификации (JWT)** — это стандартный принцип безопасности.
- **Публичными сделаны только операции, не влияющие на данные** — просмотр каталога, получение информации о книге.
- Такой подход минимизирует поверхность атаки и делает проект совместимым с лучшими практиками безопасности веб-приложений.

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
# Установите зависимости
pip install -r requirements.txt

# Запустите все тесты
pytest -v

# Получить отчёт о покрытии кода (если установлен pytest-cov)
pytest --cov=app tests/
```
### Стратегия покрытия

- Покрываются не только “счастливые” сценарии, но и бизнес-ограничения (лимиты, ошибки, повторные возвраты).
- Покрытие бизнес-логики — 95% 
---
