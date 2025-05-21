from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.book import Book
from app.models.reader import Reader
from app.models.loan import Loan
from app.schemas.loan import LoanCreate, LoanReturn
from app.utils import get_by_id_or_404, get_by_filter_or_404

class LoanService:
    """
    Service for managing book loans.
    """

    @staticmethod
    def create_loan(db: Session, loan_in: LoanCreate) -> Loan:
        """
        Create a new loan for a book and a reader.
        """
        book = get_by_id_or_404(db, Book, loan_in.book_id)
        if book.copies < 1:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="No copies available for this book"
            )
        # Raise HTTPException if reader does not exist
        get_by_id_or_404(db, Reader, loan_in.reader_id)

        # Check the reader's current active loans (not returned)
        active_loans = db.query(Loan).filter(
            Loan.reader_id == loan_in.reader_id,
            Loan.return_date.is_(None)
        ).count()
        if active_loans >= 3:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Reader has already borrowed 3 books"
            )
        # Register the loan and update book copies
        book.copies -= 1
        loan = Loan(
            book_id=loan_in.book_id,
            reader_id=loan_in.reader_id
        )
        db.add(loan)
        db.commit()
        db.refresh(loan)
        return loan

    @staticmethod
    def return_loan(db: Session, loan_in: LoanReturn) -> Loan:
        """
        Return a borrowed book.
        """
        # Find an active loan for this book and reader
        loan = get_by_filter_or_404(
            db, Loan,
            Loan.book_id == loan_in.book_id,
            Loan.reader_id == loan_in.reader_id,
            Loan.return_date.is_(None),
            detail="No active loan found"
        )
        book = get_by_id_or_404(db, Book, loan.book_id)
        book.copies += 1
        loan.return_date = loan_in.return_date
        db.commit()
        db.refresh(loan)
        return loan

    @staticmethod
    def get_loans_by_reader(db: Session, reader_id: int):
        """
        Get all current (not returned) loans for a reader.
        """
        # Raise HTTPException if reader does not exist
        get_by_id_or_404(db, Reader, reader_id)
        return db.query(Loan).filter(
            Loan.reader_id == reader_id,
            Loan.return_date.is_(None)
        ).all()
