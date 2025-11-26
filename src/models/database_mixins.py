from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy_mixins.repr import ReprMixin
from sqlalchemy_mixins.serialize import SerializeMixin

from src.schemas.SchemaMixins import TaskAndProjectStatuses


class Base(DeclarativeBase):
    __abstract__ = True


class DatabaseBaseModel(Base, ReprMixin, SerializeMixin):
    __abstract__ = True
    __repr__ = ReprMixin.__repr__

    pass


class HasId:
    """Defines common fields for all database_manager models"""

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)


class HasCreatedAndUpdateTimestamps:
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.now(tz=timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(tz=timezone.utc),
        onupdate=datetime.now(tz=timezone.utc),
        nullable=False,
    )


class HasOptionalStartAndDeadlineDates:
    deadline_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    start_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )


class HasTaskOrProjectStatus:
    status: Mapped[TaskAndProjectStatuses] = mapped_column(
        nullable=False, default=TaskAndProjectStatuses.not_started
    )
