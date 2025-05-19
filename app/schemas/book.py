from typing import Optional
from pydantic import BaseModel, Field


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
