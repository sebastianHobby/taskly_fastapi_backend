import uuid

from sqlalchemy import String, Column, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.models.DatabaseBaseModel import DatabaseBaseModel
from src.schemas.MixinSchemas import HasStartDateAndDeadline


class Task(DatabaseBaseModel, HasStartDateAndDeadline):
    __tablename__ = "tasks"
    name: Mapped[str]
    description: Mapped[str] = mapped_column(String, nullable=True)
    is_complete = Column(Boolean, nullable=False, default=False)
    parent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("task_containers.uuid"), nullable=True
    )
