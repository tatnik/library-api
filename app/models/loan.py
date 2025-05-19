from sqlalchemy import Column, Integer, DateTime, ForeignKey, func, CheckConstraint
from sqlalchemy.orm import relationship
from app.db import Base
from .mixins import TimestampMixin


class Loan(Base, TimestampMixin):
    __tablename__ = 'loans'
    __table_args__ = (
        CheckConstraint(
            '(return_date IS NULL) OR (return_date >= loan_date)',
            name='ck_loans_return_date'
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    reader_id = Column(Integer, ForeignKey('readers.id'), nullable=False)
    loan_date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    return_date = Column(DateTime(timezone=True), nullable=True)

    book = relationship('Book', back_populates='loans')
    reader = relationship('Reader', back_populates='loans')

    def __repr__(self):
        return (
            f"<Loan(id={self.id}, book_id={self.book_id}, reader_id={self.reader_id})>"
        )
