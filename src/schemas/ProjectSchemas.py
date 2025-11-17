from datetime import datetime
from uuid import UUID

import pydantic

from src.schemas.MixinSchemas import TaskContainerTypes
from src.schemas.TaskContainerSchemas import (
    TaskContainerGet,
    TaskContainerCreate,
    TaskContainerUpdate,
)


class ProjectGet(TaskContainerGet):
    is_complete: bool
    deadline_date: datetime | None = None
    start_date: datetime | None = None
    type: TaskContainerTypes


class ProjectCreate(TaskContainerCreate):
    model_config = pydantic.ConfigDict(from_attributes=True)
    is_complete: bool | None = False
    deadline_date: datetime | None = None
    start_date: datetime | None = None


class ProjectUpdate(TaskContainerUpdate):
    # Mandatory fields: Id + values
    is_complete: bool
    deadline_date: datetime | None = None
    start_date: datetime | None = None
