from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.loan import LoanCreate, LoanRead, LoanReturn
from app.schemas.book import BookRead
from app.services.loan_service import LoanService
from app.core.security import get_current_user
from app.db import get_db

router = APIRouter(
    prefix="/loans",
    tags=["loans"],
    dependencies=[Depends(get_current_user)]
)

@router.post(
    "/",
    response_model=LoanRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new loan"
)
def create_loan(
    loan_in: LoanCreate,
    db: Session = Depends(get_db)
) -> LoanRead:
    """
    Loan a book to a reader.
    """
    return LoanService.create_loan(db, loan_in)

@router.post(
    "/return",
    response_model=LoanReturn,
    summary="Return a loaned book"
)
def return_loan(
    loan_in: LoanReturn,
    db: Session = Depends(get_db)
) -> LoanRead:
    """
    Return a loaned book.
    """
    return LoanService.return_loan(db, loan_in)

@router.get(
    "/{reader_id}",
    response_model=List[LoanRead],
    summary="Active loan list by reader"
)
def get_loans_by_reader(
    reader_id: int,
    db: Session = Depends(get_db)
) -> List[LoanRead]:
    """
    Get all currently loaned books for a reader.
    """
    return LoanService.get_loans_by_reader(db, reader_id)
