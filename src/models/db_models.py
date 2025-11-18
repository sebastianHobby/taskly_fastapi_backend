import uuid
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, ForeignKey, Column, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

from src.schemas.MixinSchemas import HasStartDateAndDeadline, TaskContainerTypes


class DatabaseBaseModel(DeclarativeBase):
    """Defines common fields for all database models"""

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}

    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=func.now())
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)


class TaskContainer(DatabaseBaseModel):
    __tablename__ = "task_containers"

    name: Mapped[str]
    description: Mapped[str] = mapped_column(String, nullable=True)
    last_reviewed_date: Mapped[datetime] = mapped_column(
        nullable=True
    )  # Last user review of this task container
    # Self reference i.e. Adjacent list design pattern for hierarchy structure
    parent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("task_containers.uuid"), nullable=True
    )
    children = relationship("TaskContainer")
    # Discriminator attribute
    type: Mapped[TaskContainerTypes]
    __mapper_args__ = {
        "polymorphic_identity": "task_containers",
        "polymorphic_on": "type",
    }


class Project(TaskContainer, HasStartDateAndDeadline):
    # Tell SQL alchemy to refer to this table when Area.type = project
    __mapper_args__ = {
        "polymorphic_identity": TaskContainerTypes.project,
    }
    # Project specific fields

    is_complete: Mapped[bool] = mapped_column(default=False)


class Task(DatabaseBaseModel, HasStartDateAndDeadline):
    __tablename__ = "tasks"
    name: Mapped[str]
    description: Mapped[str] = mapped_column(String, nullable=True)
    is_complete = Column(Boolean, nullable=False, default=False)
    parent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("task_containers.uuid"), nullable=True
    )


class Area(TaskContainer):
    # Tell SQL alchemy to refer to this table when task_container.type = project
    __mapper_args__ = {"polymorphic_identity": TaskContainerTypes.area}
