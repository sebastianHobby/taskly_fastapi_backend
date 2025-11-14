# Database models
import uuid

from sqlalchemy import TIMESTAMP, Column, String, Boolean, types, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..core.database import Base


class Task(Base):
    __tablename__ = "tasks"
    # Generic fields common to all tables
    id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid, primary_key=True, default=uuid.uuid4
    )
    createdAt = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updatedAt = Column(TIMESTAMP(timezone=True), default=None, onupdate=func.now())

    # Task specific fields
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_complete = Column(Boolean, nullable=False, default=True)
    deadline_date = Column(TIMESTAMP(timezone=True), default=None)

    # Todo consider changing this design so instead
    # of 2 database fields for area_id and parent_id
    # we have parent type + ID
    # Downside is database can not enforce integrity with foreign key links
    # Plus side is you can do this via application logic AND
    # you can add new types easily - e.g. task as parent
    # You can also expand this to projects/other items in future
    # with validation logic to say X type can have A,B,C parents types

    # Foreign keys - task can be stored under project OR area
    area_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("areas_table.id"), nullable=True
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects_table.id"), nullable=True
    )
