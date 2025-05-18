from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
import app.security as security
from app.db import get_db

router = APIRouter(
    tags=["Readers"],
    dependencies=[Depends(security.get_current_user)] 
)


def get_reader_or_404(
    reader_id: int,
    db: Session
) -> models.Reader:
    reader = db.query(models.Reader).filter(models.Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reader not found"
        )
    return reader

@router.post("/", response_model=schemas.ReaderRead, status_code=status.HTTP_201_CREATED)
def create_reader(
    reader_in: schemas.ReaderCreate,
    db: Session = Depends(get_db)
) -> models.Reader:
    if db.query(models.Reader).filter(models.Reader.email == reader_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    reader = models.Reader(name=reader_in.name, email=reader_in.email)
    db.add(reader)
    db.commit()
    db.refresh(reader)
    return reader

@router.get("/", response_model=List[schemas.ReaderRead])
def read_readers(
    db: Session = Depends(get_db)
) -> List[models.Reader]:
    return db.query(models.Reader).all()

@router.get("/{reader_id}", response_model=schemas.ReaderRead)
def read_reader(
    reader_id: int,
    db: Session = Depends(get_db)
) -> models.Reader:
    return get_reader_or_404(reader_id, db)

@router.put("/{reader_id}", response_model=schemas.ReaderRead)
def update_reader(
    reader_id: int,
    reader_in: schemas.ReaderUpdate,
    db: Session = Depends(get_db)
) -> models.Reader:
    reader = get_reader_or_404(reader_id, db)
    for field, value in reader_in.dict(exclude_unset=True).items():
        setattr(reader, field, value)
    db.commit()
    db.refresh(reader)
    return reader

@router.delete("/{reader_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reader(
    reader_id: int,
    db: Session = Depends(get_db)
) -> None:
    reader = get_reader_or_404(reader_id, db)
    db.delete(reader)
    db.commit()
    return
