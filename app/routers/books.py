from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.services.book_service import BookService
from app.core.security import get_current_user
from app.utils import get_by_id_or_404
from app.models.book import Book
from app.db import get_db

router = APIRouter(
    prefix="/books",
    tags=["books"],
)

@router.get(
    "/",
    response_model=List[BookRead],
    summary="Book list"
)
def read_books(
    db: Session = Depends(get_db)
) -> List[BookRead]:
    """
    Get a list of all books.
    """
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
    """
    Get a single book by its ID.
    """
    return get_by_id_or_404(db, Book, book_id)

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
    """
    Add a new book to the catalog.
    """
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
    """
    Update the data of a book by ID.
    """
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
    """
    Delete a book by its ID.
    """
    BookService.delete_book(db, book_id)
