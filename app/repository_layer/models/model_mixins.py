from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4

import sqlalchemy
from sqlalchemy import TIMESTAMP, Interval, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.repository_layer.models.enumerations import (
    TaskAndProjectStatuses,
    RepeatIntervalType,
)


class HasCommonFields:
    """Defines common fields for all database_manager models
    Note the SearchRepository class depends on these"""

    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
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


class HasRepeatFields:
    repeat_interval_type: Mapped[RepeatIntervalType] = mapped_column(nullable=True)
    repeat_interval: Mapped[timedelta] = mapped_column(Interval, nullable=True)
    repeat_start: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
    )
    repeat_end: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
    )


class HasOptionalStartAndDeadlineDates:
    deadline_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    start_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )


class HasOptionalDescription:
    description = sqlalchemy.Column(sqlalchemy.String, nullable=False)


class HasStatus:
    status: Mapped[TaskAndProjectStatuses] = mapped_column(
        nullable=False, default=TaskAndProjectStatuses.not_started
    )
