from typing import Optional
from pydantic import BaseModel, EmailStr


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
