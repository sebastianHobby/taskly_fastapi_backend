from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import String, ForeignKey, TIMESTAMP, Index, func
from sqlalchemy.ext.indexable import index_property
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from src.schemas.SchemaMixins import TaskAndProjectStatuses

from sqlalchemy.dialects.postgresql import TSVECTOR


class DatabaseBaseModel(DeclarativeBase):
    pass


class HasId:
    """Defines common fields for all database models"""

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)


class HasForeignKeyGroupId:
    group_id: Mapped[UUID] = mapped_column(ForeignKey("groups.id"), nullable=False)


class HasForeignKeyTasklistId:
    list_id: Mapped[UUID] = mapped_column(ForeignKey("tasklist.id"), nullable=False)


class HasCreatedAndUpdateTimestamps:
    created_datetime: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.now(tz=timezone.utc), nullable=False
    )
    updated_datetime: Mapped[datetime] = mapped_column(
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


class HasNameAndOptionalDescription:
    name: Mapped[str] = mapped_column(TSVECTOR, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)


class HasTaskOrProjectStatus:
    status: Mapped[TaskAndProjectStatuses] = mapped_column(
        nullable=False, default=TaskAndProjectStatuses.not_started
    )
