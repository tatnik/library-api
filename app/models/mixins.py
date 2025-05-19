from sqlalchemy import Column, DateTime, func


class TimestampMixin:
    """
    Добавляет поля created_at и updated_at во все модели, наследующие миксин.
    """
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
