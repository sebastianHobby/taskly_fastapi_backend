import uuid
from datetime import datetime

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.DatabaseBaseModel import DatabaseBaseModel
from src.schemas.MixinSchemas import TaskContainerTypes


# Base class defining what a task container looks like
# Container examples might be Areas , projects etc
# SQL alchemy framewok sets up single table inheritance
# model to match class hierachy defined here with TaskContainer + Children
# See https://docs.sqlalchemy.org/en/20/orm/inheritance.html
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
