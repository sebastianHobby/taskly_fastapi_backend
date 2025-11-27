from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from app.repository_layer.models.enumerations import TaskAndProjectStatuses


class HasCommonFields:
    """Defines common fields for all database_manager models"""

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
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


class HasStatus:
    status: Mapped[TaskAndProjectStatuses] = mapped_column(
        nullable=False, default=TaskAndProjectStatuses.not_started
    )
