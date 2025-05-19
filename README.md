# Library API

**RESTful API для управления библиотечным каталогом**

---

## 🎯 Инструкция по запуску

1. **Клонирование репозитория**

   ```bash
   git clone https://github.com/tatnik/library-api
   cd library-api
   ```

2. **Создание `.env`** (в корне проекта):

   ```dotenv
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=library_db
   DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/library_db
   SECRET_KEY=your_super_secret_key
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
3. **Создание папок для служебных данных**

   ```bash
   mkdir data
   cd data
   mkdir postgres       # том для Postgres на хосте
   mkdir tests          # папка для локальных копий базы данных, используемых для тестов
   ```


4. **Запуск через Docker Compose**

   ```bash
 
   docker-compose up -d --build
   ```

5. **Первичная регистрация**

   * Откройте `http://localhost:8000/docs`
   * В разделе **Auth** выполните `POST /auth/register` с JSON:

     ```json
     {"email": "admin@example.com", "password": "strongpass"}
     ```
   * Далее выполните `POST /auth/login` (form-data) и получите `access_token`.

---

## 📁 Структура проекта

```
library-api/
├── .env               
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── dockerfile
├── pytest.ini
├── README.md
├── requirements.txt

├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── app/
│   ├── main.py           # точка входа FastAPI
│   ├── db.py             # SQLAlchemy engine, Session, Base, get_db
│   ├── models.py         # ORM-модели: User, Book, Reader, BorrowedBook
│   ├── schemas.py        # Pydantic-схемы
│   ├── security.py       # JWT, пароли, deps
│   ├── core/config.py    # Pydantic Settings
│   └── routers/
│       ├── auth.py       # регистрация, логин, logout, me
│       ├── books.py      # CRUD книг + публичные GET + список невозвращенных читателем книг
│       ├── readers.py    # CRUD читателей
│       └── borrow.py     # выдача и возврат книг + список невозвращенных читателем книг
├── data/
│   ├── postgres
│   └── tests
└── tests/
    ├── test_auth.py
    ├── test_books.py
    ├── test_borrow.py
    ├── test_db_shema.py
    └── test_readers.py
```

---

## 🗄️ Структура базы данных

* **users**: хранит библиотекарей (`email`, `hashed_password`, `is_active`).
* **books**: каталог книг (`title`, `author`, `published_year`, `isbn`, `copies`, `description`).
* **readers**: читатели (`name`, `email`, `phone`).
* **borrowed_books**: история выдачи книг (`book_id`, `reader_id`, `borrow_date`, `return_date`).
* **alembic\_version**: служебная таблица миграций.

**Решения**:

* Отдельная таблица `borrowed_books` для учёта выдачи/возврата книг, реализации ограничений по количеству выдаваемых книг, формирования списка невозвращенных книг.
* Индексы по `id`, `email` и `isbn` для производительности.

---

## ⚙️ Бизнес-логика

1. **Выдача книги** (`POST /borrow/`)

   * Проверяем, что книга есть в наличии (в таблице **books** для выбранной книги `copies > 0`). Если книги в наличии нет,  возвращаем — `400 Bad Request`.
   * Уменьшаем `copies` на 1 и создаём запись в **borrowed_books** с `return_date = NULL`.

2. **Ограничение выдачи**

   * Один читатель не может иметь более **3** выданных книг (считаем  количество записей в таблице **borrowed_books**  по `reader_id`, для которых `return_date IS NULL`).

3. **Возврат книги** (`POST /return/`)

   * В таблице **borrowed_books** ищем запись с `book_id`, `reader_id` и `return_date IS NULL`.
   * Если не найдена — `400 Bad Request`.
   * Устанавливаем `return_date = now()`,
   * В таблице **books** для записи с `id = book_id` увеличиваем `copies` на 1.

**Сложности**:

* Конкурентные запросы увеличивают сложность консистентности `copies` — решается за счёт транзакций и блокировок.
* Подсчёт выданных книг реализован через `COUNT` в SQLAlchemy.

---

## 🔒 Аутентификация

* **JWT** через `python-jose[cryptography]`.
* **Хеширование паролей** с `passlib[bcrypt]`.
* **Dependencies**:

  * `get_db()` из `app/db.py`.
  * `get_current_user` проверяет JWT (`sub` → `email`) и чёрный список отозванных токенов.
* **Защищены JWT**:

  * Создание, обновление и удаление (книг, читателей).
  * Эндпойнты выдачи/возврата книг.
  * `/readers`, `/borrow`.
* **Публичные**:

  * Чтение списка и деталей книг (`GET /books/`, `GET /books/{id}`)  — удобно для каталога

---

## 💡 Дополнительная фича: резервирование книг

Предлагается реализовать механизм резервирования книг :

* **Настройка сроков резервирования**:

  * Параметр `RESERVATION_RESERVED_DAYS` в `app/core/config.py` задаёт максимальный срок (в днях) хранения резерва.

* **Модель данных `reservations` **:

  * `id`: PK
  * `reader_id`: FK → `readers.id`
  * `book_id`: FK → `books.id`
  * `start_date`: дата создания записи (регистрирует факт желаения читателя получить книгу)
  * `reserve_date`: дата фактического резервирования (регистрирует факт возврата в библиотеку книги другим читателем и перемещение ее в резерв)
  * `expire_date`: `reserve_date + RESERVATION_RESERVED_DAYS` (до какой даты книга может оставаться в резерве)
  * `notify_date`: дата/время отправки уведомления читателю (NULL до уведомления)
  * `status`: ENUM(`PENDING`,`RESERVED`. `NOTIFIED`, `COMPLETED`, `CANCELLED`, `EXPIRED`)

* **Поток работы**:

  1. **Создание wish-записи**: для отсутствующей в наличии книги (`copies == 0`)  в таблице `reservations` создаём запись со статусом `PENDING` и `start_date` = текущая дата
  2. **Возврат книги** : при возврате проверяем наличие активных резервов в статусе `PENDING`, берём самый старый, изменяем `reserve_date` на  текущую дату. Изменяем статус на `RESERVED`. Значение `copies` в таблице `books` не изменяем. 
  3. **Уведомление читателей** : может выполняться по расписанию. Из таблицы `reservations` выбираются все записи со статусом `RESERVED`. Для каждой записи в отправляется уведомление по SMS или email, в случае успешной отправки статус меняется на `NOTIFIED`, заполняется `notify_date`.
  4. **Выдача книги из резерва**: статус → `COMPLETED`, создаём запись выдачи (`borrowed_books`), `copies` при этом не дожно изменяться (можно в таблицу выдач добавить поле с пометкой, что выдача идет из резерва).
  5. **Отказ читателя от получения книги**:  статус → `CANCELLED`, в `books` **увеличиваем** `copies` на 1 (резерв снимается).
  6. **Истечение срока резерва**: 
     * Периодическая задача (Celery/cron) проверяет резервы с `expire_date < now()` в статусе `RESERVED` или `NOTIFIED`, переводит их в `EXPIRED` и **увеличивает** `copies` на 1 в таблице `books`.

* **Эндпоинты**:

  * `POST`  /reservations/add/{id_book}{id_reader}  добавить новую запись
  * `PUT`   /reservations/add/{id} изменить запись
  * `GET`   /reservations/{reader_id}{[список статусов]}` — получить все записи читателя для которых `status` в указанном списке (по умолчанию список = [RESERVED, NOTIFIED])
  * `PATCH  /reservations/notifyall/` — отправить уведомления всем (`status`=`RESERVED`)
  * `PATCH  /reservations/{id}/notify` — вручную отправить повторное уведомление (смс/email)
  * `PATCH  /reservations/{id}/complete` — оформить выдачу после прихода читателя
  * `PATCH  /reservations/{id}/cancel` — отменить резерв (читатель отказался)
  * `PATCH  /reservations/expiring` — получить все записи с истекающим сроком резерва
**Преимущества**:

* Чёткое состояние резерва (`status`), фиксация даты уведомления, времени истечения.
* Гибкость: можно добавить напоминания (повторные SMS) через задачу `notify_pending_reservations`.
* Консистентность количества копий благодаря централизованной логике изменения в CRUD и фоновых задачах.

*Идея реализации*: использовать Celery или APScheduler для фоновых задач: отправки уведомлений и закрытия просроченных резервов.
дополнительно необходимо выполнять периодическую очистку таблицы от старых записей с закрытыми резервами
