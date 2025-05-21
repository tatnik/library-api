from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.reader import ReaderCreate, ReaderRead, ReaderUpdate
from app.services.reader_service import ReaderService
from app.core.security import get_current_user
from app.utils import get_by_id_or_404
from app.models.reader import Reader
from app.db import get_db

router = APIRouter(
    prefix="/readers",
    tags=["readers"],
    dependencies=[Depends(get_current_user)]
)

@router.post(
    "/",
    response_model=ReaderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new reader"
)
def create_reader(
    reader_in: ReaderCreate,
    db: Session = Depends(get_db)
) -> ReaderRead:
    """
    Add a new reader.
    """
    return ReaderService.create_reader(db, reader_in)

@router.get(
    "/",
    response_model=List[ReaderRead],
    summary="List all readers"
)
def read_readers(
    db: Session = Depends(get_db)
) -> List[ReaderRead]:
    """
    Get a list of all readers.
    """
    return ReaderService.list_readers(db)

@router.get(
    "/{reader_id}",
    response_model=ReaderRead,
    summary="Get a reader by ID"
)
def read_reader(
    reader_id: int,
    db: Session = Depends(get_db)
) -> ReaderRead:
    """
    Get a single reader by ID.
    """
    return get_by_id_or_404(db, Reader, reader_id)

@router.put(
    "/{reader_id}",
    response_model=ReaderRead,
    summary="Update a reader"
)
def update_reader(
    reader_id: int,
    reader_in: ReaderUpdate,
    db: Session = Depends(get_db)
) -> ReaderRead:
    """
    Update the data of a reader by ID.
    """
    return ReaderService.update_reader(db, reader_id, reader_in)

@router.delete(
    "/{reader_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a reader"
)
def delete_reader(
    reader_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a reader by ID.
    """
    ReaderService.delete_reader(db, reader_id)
