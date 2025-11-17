from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.types import Uuid
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql import func


class DatabaseBaseModel(DeclarativeBase):
    """Defines common fields for all database models"""

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}

    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=func.now())
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
