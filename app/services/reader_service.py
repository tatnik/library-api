from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.reader import Reader
from app.schemas.reader import ReaderCreate, ReaderUpdate


class ReaderService:
    """
    Business logic for managing readers.
    """
    @staticmethod
    def get_reader_or_404(db: Session, reader_id: int) -> Reader:
        reader = db.query(Reader).get(reader_id)
        if not reader:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reader not found"
            )
        return reader

    @staticmethod
    def create_reader(db: Session, reader_in: ReaderCreate) -> Reader:
        if db.query(Reader).filter(Reader.email == reader_in.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        reader = Reader(**reader_in.dict())
        db.add(reader)
        db.commit()
        db.refresh(reader)
        return reader

    @staticmethod
    def list_readers(db: Session) -> List[Reader]:
        return db.query(Reader).all()

    @staticmethod
    def update_reader(db: Session, reader_id: int, reader_in: ReaderUpdate) -> Reader:
        reader = ReaderService.get_reader_or_404(db, reader_id)
        for field, value in reader_in.dict(exclude_unset=True).items():
            setattr(reader, field, value)
        db.commit()
        db.refresh(reader)
        return reader

    @staticmethod
    def delete_reader(db: Session, reader_id: int) -> None:
        reader = ReaderService.get_reader_or_404(db, reader_id)
        db.delete(reader)
        db.commit()
