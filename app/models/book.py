from sqlalchemy import (
    Column, Integer, String, Text, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from app.db import Base
from .mixins import TimestampMixin


class Book(Base, TimestampMixin):
    __tablename__ = 'books'
    __table_args__ = (
        UniqueConstraint('isbn', name='uq_books_isbn'),
        CheckConstraint('copies >= 0', name='ck_books_copies_non_negative'),
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    published_year = Column(Integer, CheckConstraint('published_year >= 0'), nullable=True)
    isbn = Column(String(20), nullable=True, index=True)
    copies = Column(Integer, default=1, nullable=False)
    description = Column(Text, nullable=True)

    loans = relationship(
        'Loan', back_populates='book', cascade='all, delete-orphan'
    )


    def __repr__(self):
        return f"<Book(id={self.id}, title={self.title!r})>"
