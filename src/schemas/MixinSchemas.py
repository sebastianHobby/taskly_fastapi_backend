from enum import Enum
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column


class HasStartDateAndDeadline:
    deadline_date: Mapped[datetime] = mapped_column(nullable=True)
    start_date: Mapped[datetime] = mapped_column(nullable=True)


class TaskContainerTypes(Enum):
    project = "project"
    area = "area"
