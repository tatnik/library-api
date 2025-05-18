from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import app.schemas as schemas
import app.models as models
import app.security as security
from app.db import get_db
from datetime import datetime

router = APIRouter(
    prefix="",
    tags=["Borrow"],
    dependencies=[Depends(security.get_current_user)]
)

# Вспомогательная функция для получения активных займов читателя
def count_active_loans(reader_id: int, db: Session) -> int:
    return db.query(models.BorrowedBook).filter(
        models.BorrowedBook.reader_id == reader_id,
        models.BorrowedBook.return_date.is_(None)
    ).count()

@router.post("/borrow/", response_model=schemas.BorrowRead)
def borrow_book(
    payload: schemas.BorrowCreate,
    db: Session = Depends(get_db)
) -> models.BorrowedBook:
    book = db.query(models.Book).filter(models.Book.id == payload.book_id).first()
    if not book or book.copies < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No copies available")
    if count_active_loans(payload.reader_id, db) >= 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Loan limit exceeded")
    # Выдача
    book.copies -= 1
    borrow = models.BorrowedBook(book_id=payload.book_id, reader_id=payload.reader_id)
    db.add(borrow)
    db.commit(); db.refresh(borrow)
    return borrow

@router.post("/return/", response_model=schemas.BorrowRead)
def return_book(
    payload: schemas.BorrowCreate,
    db: Session = Depends(get_db)
) -> models.BorrowedBook:
    loan = db.query(models.BorrowedBook).filter(
        models.BorrowedBook.book_id == payload.book_id,
        models.BorrowedBook.reader_id == payload.reader_id,
        models.BorrowedBook.return_date.is_(None)
    ).first()
    if not loan:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active loan found")
    loan.return_date = datetime.utcnow()
    book = db.query(models.Book).filter(models.Book.id == payload.book_id).first()
    book.copies += 1
    db.commit(); db.refresh(loan)
    return loan
