from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.services.book_service import BookService
from app.core.security import get_current_user
from app.db import get_db

router = APIRouter(
    prefix="/books",
    tags=["books"],
)

@router.get(
    "/",
    response_model=List[BookRead],
    summary="List all books"
)
def read_books(
    db: Session = Depends(get_db)
) -> List[BookRead]:
    """Получение списка всех книг"""
    return BookService.list_books(db)

@router.get(
    "/{book_id}",
    response_model=BookRead,
    summary="Get a book by ID"
)
def read_book(
    book_id: int,
    db: Session = Depends(get_db)
) -> BookRead:
    """Получение одной книги по ID"""
    return BookService.get_book_or_404(db, book_id)

@router.post(
    "/",
    response_model=BookRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book",
    dependencies=[Depends(get_current_user)]
)
def create_book(
    book_in: BookCreate,
    db: Session = Depends(get_db)
) -> BookRead:
    """Добавление новой книги в каталог"""
    return BookService.create_book(db, book_in)

@router.put(
    "/{book_id}",
    response_model=BookRead,
    summary="Update a book",
    dependencies=[Depends(get_current_user)]
)
def update_book(
    book_id: int,
    book_in: BookUpdate,
    db: Session = Depends(get_db)
) -> BookRead:
    """Изменение данных книги по ID"""
    return BookService.update_book(db, book_id, book_in)

@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a book",
    dependencies=[Depends(get_current_user)]
)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db)
) -> None:
    """Удаление книги по ID"""
    BookService.delete_book(db, book_id)
