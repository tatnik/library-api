from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate, BookRead

class BookService:
    """
    Business logic for managing books.
    """
    @staticmethod
    def list_books(db: Session) -> List[BookRead]:
        return db.query(Book).all()

    @staticmethod
    def get_book_or_404(db: Session, book_id: int) -> BookRead:
        book = db.get(Book, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        return book

    @staticmethod
    def create_book(db: Session, book_in: BookCreate) -> BookRead:
        book = Book(**book_in.dict(exclude_none=True))
        db.add(book)
        db.commit()
        db.refresh(book)
        return book

    @staticmethod
    def update_book(db: Session, book_id: int, book_in: BookUpdate) -> BookRead:
        book = BookService.get_book_or_404(db, book_id)
        for field, value in book_in.dict(exclude_unset=True).items():
            setattr(book, field, value)
        db.commit()
        db.refresh(book)
        return book

    @staticmethod
    def delete_book(db: Session, book_id: int) -> None:
        book = BookService.get_book_or_404(db, book_id)
        db.delete(book)
        db.commit()
