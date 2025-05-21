from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class LoanBase(BaseModel):
    book_id: int
    reader_id: int


class LoanCreate(LoanBase):
    pass


class LoanUpdate(BaseModel):
    return_date: Optional[datetime]


class LoanRead(LoanBase):
    id: int
    loan_date: datetime
    return_date: Optional[datetime] = None

    class Config:
        orm_mode = True

class LoanReturn(BaseModel):
    book_id: int
    reader_id: int
    return_date: Optional[datetime] = None
    class Config:
        orm_mode = True
