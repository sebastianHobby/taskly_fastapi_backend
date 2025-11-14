# Database models
import typing
import uuid

from sqlalchemy import TIMESTAMP, Column, String, Boolean, types, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base


# The code below uses SqlAlchemy to define models which follow the
# Class table inheritance pattern aka joined table inheritance
# See https://ruheni.dev/writing/sql-table-inheritance/ and
# https://ruheni.dev/writing/sql-table-inheritance/ for background


class TaskContainer(Base):
    __tablename__ = "task_containers"

    # Variables shared by all instances of TaskContainer and its child classes
    id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid, primary_key=True, default=uuid.uuid4
    )
    createdAt = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updatedAt = Column(TIMESTAMP(timezone=True), default=None, onupdate=func.now())
    name: Mapped[str]

    # Defining parent id here allows all sub types to have a parent of any
    # task_container_type. SQL will perform a self join aka it will
    # use the adjacency list design pattern https://docs.sqlalchemy.org/en/20/orm/self_referential.html
    parent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("task_containers.id"))
    children = relationship("TaskContainer")
    # Discriminator attribute
    type: Mapped[str]

    __mapper_args__ = {
        "polymorphic_identity": "task_containers",
        "polymorphic_on": "type",
    }


# Projects extends area base table / class
class Area(TaskContainer):
    __tablename__ = "areas"
    # Link to superset parent table
    id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("task_containers.id"), primary_key=True
    )
    # Tell SQL alchemy to refer to this table when Area.type = project
    __mapper_args__ = {
        "polymorphic_identity": "areas",
    }


class Project(TaskContainer):
    __tablename__ = "projects"
    # Link to superset parent table
    id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("task_containers.id"), primary_key=True
    )
    # Tell SQL alchemy to refer to this table when Area.type = project
    __mapper_args__ = {
        "polymorphic_identity": "projects",
    }

    # Project specific fields
    deadline_date = Column(TIMESTAMP(timezone=True), default=None)
    is_complete = Column(Boolean, nullable=False, default=True)
    colour = Column(String, nullable=True)
    # Last user review of this project
    last_reviewed_date = Column(TIMESTAMP(timezone=True), default=None)


# Areas - Life values or areas (e.g. Family/Friends , role of Parent, Career)
# class Area(Base):
#     __tablename__ = "areas_table"
#     # Generic table fields common to all models
#     id: Mapped[uuid.UUID] = mapped_column(
#         types.Uuid, primary_key=True, default=uuid.uuid4
#     )
#     createdAt = Column(
#         TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
#     )
#     updatedAt = Column(TIMESTAMP(timezone=True), default=None, onupdate=func.now())
#
#     name = Column(String, nullable=False)
#     # SQL alchemy requires parent/child object to both define relationship between tables
#     child_projects: Mapped[typing.List["Project"]] = relationship()
#     child_tasks: Mapped[typing.List["Task"]] = relationship()
#
#
# # Projects - Groups of tasks required to achieve a specific goal
# class Project(Base):
#     __tablename__ = "projects_table"
#
#     # Generic table fields common to all models
#     id: Mapped[uuid.UUID] = mapped_column(
#         types.Uuid, primary_key=True, default=uuid.uuid4
#     )
#     createdAt = Column(
#         TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
#     )
#     updatedAt = Column(TIMESTAMP(timezone=True), default=None, onupdate=func.now())
#
#     # Project specific fields
#     name = Column(String, nullable=False)
#     description = Column(String, nullable=True)
#     deadline_date = Column(TIMESTAMP(timezone=True), default=None)
#     is_complete = Column(Boolean, nullable=False, default=True)
#     colour = Column(String, nullable=True)
#     # Last user review of this project
#     last_reviewed_date = Column(TIMESTAMP(timezone=True), default=None)
#
#     # Foreign keys
#     area_id: Mapped[uuid.UUID | None] = mapped_column(
#         ForeignKey("areas_table.id"), nullable=True
#     )
