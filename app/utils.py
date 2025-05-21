from fastapi import HTTPException, status
from sqlalchemy.orm import Session

def get_by_id_or_404(
    db: Session,
    model,
    object_id,
    detail: str = None,
    status_code=status.HTTP_400_BAD_REQUEST
):
    """
    Query the DB for an object by primary key and raise HTTPException if not found.
    """
    obj = db.get(model, object_id)
    if not obj:
        if not detail:
            detail = f"{model.__name__} with id={object_id} not found"
        raise HTTPException(status_code, detail=detail)
    return obj

def get_by_filter_or_404(
    db: Session,
    model,
    *filter_conditions,
    detail: str = None,
    status_code=status.HTTP_400_BAD_REQUEST
):
    """
    Query the DB for an object using filter conditions and raise HTTPException if not found.
    """
    obj = db.query(model).filter(*filter_conditions).first()
    if not obj:
        if not detail:
            detail = f"{model.__name__} not found"
        raise HTTPException(status_code, detail=detail)
    return obj
