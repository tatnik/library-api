from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
import app.security as security
from app.db import get_db

router = APIRouter(
    tags=["Books"],
)

#--- Хелпер для получения книги или выброса 404
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

#--- Публичные эндпойнты
@router.get("/", response_model=List[schemas.BookRead])
def read_books(
    db: Session = Depends(get_db)
) -> List[models.Book]:
    """ Получение списка всех книг """
    return db.query(models.Book).all()

@router.get("/{book_id}", response_model=schemas.BookRead)
def read_book(
    book_id: int,
    db: Session = Depends(get_db)
) -> models.Book:
    """ Получение одной книги по ID """
    return get_book_or_404(book_id, db)

#--- Защищённые JWT операции
@router.post("/", response_model=schemas.BookRead, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(security.get_current_user)])
def create_book(
    book_in: schemas.BookCreate,
    db: Session = Depends(get_db)
) -> models.Book:
    """ Добавление новой книги в каталог """
    book = models.Book(**book_in.dict(exclude_none=True))
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@router.put("/{book_id}", response_model=schemas.BookRead,
            dependencies=[Depends(security.get_current_user)])
def update_book(
    book_id: int,
    book_in: schemas.BookUpdate,
    db: Session = Depends(get_db)
) -> models.Book:
    """ Изменение данных книги по ID"""
    book = get_book_or_404(book_id, db)
    for field, value in book_in.dict(exclude_unset=True).items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT,
            dependencies=[Depends(security.get_current_user)])
def delete_book(
    book_id: int,
    db: Session = Depends(get_db)
) -> None:
    """ Удаление книги по ID"""
    book = get_book_or_404(book_id, db)
    db.delete(book)
    db.commit()
    return
