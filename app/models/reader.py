from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base
from .mixins import TimestampMixin


class Reader(Base, TimestampMixin):
    __tablename__ = 'readers'
    __table_args__ = (
        UniqueConstraint('email', name='uq_readers_email'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone_number = Column(String(20), nullable=True)

    loans = relationship(
        'Loan', back_populates='reader', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Reader(id={self.id}, name={self.name!r})>"
