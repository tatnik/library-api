from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.loan import Loan
from app.models.book import Book
from app.schemas.loan import LoanCreate
from app.schemas.book import BookRead

class LoanService:
    """
    Business logic for loans: creating and returning.
    """
    MAX_LOANS = 3

    @staticmethod
    def count_active_loans(db: Session, reader_id: int) -> int:
        """Count how many books a reader currently has on loan."""
        return db.query(Loan).filter(
            Loan.reader_id == reader_id,
            Loan.return_date.is_(None)
        ).count()

    @staticmethod
    def create_loan(db: Session, loan_in: LoanCreate) -> Loan:
        """Create a loan if copies are available and reader under the limit."""
        book = db.query(Book).get(loan_in.book_id)
        if not book or book.copies < 1:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="No copies available"
            )
        if LoanService.count_active_loans(db, loan_in.reader_id) >= LoanService.MAX_LOANS:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Loan limit exceeded"
            )
        book.copies -= 1
        loan = Loan(book_id=loan_in.book_id, reader_id=loan_in.reader_id)
        db.add(loan)
        db.commit()
        db.refresh(loan)
        return loan

    @staticmethod
    def return_loan(db: Session, loan_in: LoanCreate) -> Loan:
        """Mark a loan as returned and increment book copies."""
        loan = db.query(Loan).filter(
            Loan.book_id == loan_in.book_id,
            Loan.reader_id == loan_in.reader_id,
            Loan.return_date.is_(None)
        ).first()
        if not loan:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="No active loan found"
            )
        loan.return_date = datetime.utcnow()
        book = db.query(Book).get(loan_in.book_id)
        book.copies += 1
        db.commit()
        db.refresh(loan)
        return loan

    @staticmethod
    def get_active_loans(db: Session, reader_id: int) -> List[BookRead]:
        """Return list of books currently on loan to a reader."""
        loans = db.query(Loan).filter(
            Loan.reader_id == reader_id,
            Loan.return_date.is_(None)
        ).all()
        book_ids = [loan.book_id for loan in loans]
        return db.query(Book).filter(Book.id.in_(book_ids)).all()
