from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

# --- Auth Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserRead(BaseModel):  # схема для ответа при регистрации
    id: int
    email: EmailStr
    class Config:
        orm_mode = True
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- Book Schemas ---
class BookBase(BaseModel):
    title: str
    author: str
    published_year: Optional[int] = None
    isbn: Optional[str] = None
    copies: int = Field(1, ge=0)
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str]
    author: Optional[str]
    published_year: Optional[int]
    isbn: Optional[str]
    copies: Optional[int] = Field(None, ge=0)
    description: Optional[str]

class BookRead(BookBase):
    id: int
    class Config:
        orm_mode = True

# --- Reader Schemas ---
class ReaderBase(BaseModel):
    name: str
    email: EmailStr
    phone: str

class ReaderCreate(ReaderBase):
    pass

class ReaderUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]

class ReaderRead(ReaderBase):
    id: int
    class Config:
        orm_mode = True

# --- Borrow Schemas ---
class BorrowBase(BaseModel):
    book_id: int
    reader_id: int

class BorrowCreate(BorrowBase):
    pass

class BorrowRead(BorrowBase):
    id: int
    borrow_date: datetime
    return_date: Optional[datetime] = None
    class Config:
        orm_mode = True
