# models/user.py
from sqlalchemy import Column, Integer, String, Boolean, UniqueConstraint
from app.db import Base
from .mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = 'users'
    __table_args__ = (
        UniqueConstraint('email', name='uq_users_email'),
    )

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email!r})>"
