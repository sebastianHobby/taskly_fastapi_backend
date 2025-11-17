from sqlalchemy.orm import Mapped, mapped_column

from src.models.TaskContainerModel import TaskContainer
from src.schemas.MixinSchemas import HasStartDateAndDeadline, TaskContainerTypes


class Project(TaskContainer, HasStartDateAndDeadline):
    # Tell SQL alchemy to refer to this table when Area.type = project
    __mapper_args__ = {
        "polymorphic_identity": TaskContainerTypes.project,
    }
    # Project specific fields

    is_complete: Mapped[bool] = mapped_column(default=False)
