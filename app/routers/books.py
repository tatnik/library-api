from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
import app.security as security
from app.db import get_db

router = APIRouter(

    tags=["Books"],
    dependencies=[Depends(security.get_current_user)]  # все операции защищены JWT
)


def get_book_or_404(
    book_id: int,
    db: Session
) -> models.Book:
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book

@router.post("/", response_model=schemas.BookRead, status_code=status.HTTP_201_CREATED)
def create_book(
    book_in: schemas.BookCreate,
    db: Session = Depends(get_db)
) -> models.Book:
    book = models.Book(
        title=book_in.title,
        author=book_in.author,
        published_year=book_in.published_year,
        isbn=book_in.isbn,
        copies=book_in.copies,
        description=book_in.description
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@router.get("/", response_model=List[schemas.BookRead])
def read_books(
    db: Session = Depends(get_db)
) -> List[models.Book]:
    return db.query(models.Book).all()

@router.get("/{book_id}", response_model=schemas.BookRead)
def read_book(
    book: models.Book = Depends(lambda book_id, db=Depends(get_db): get_book_or_404(book_id, db))
) -> models.Book:
    return book

@router.put("/{book_id}", response_model=schemas.BookRead)
def update_book(
    book_id: int,
    book_in: schemas.BookUpdate,
    db: Session = Depends(get_db)
) -> models.Book:
    book = get_book_or_404(book_id, db)
    for field, value in book_in.dict(exclude_unset=True).items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db)
) -> None:
    book = get_book_or_404(book_id, db)
    db.delete(book)
    db.commit()
    return
