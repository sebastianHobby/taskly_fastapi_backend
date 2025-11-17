from uuid import UUID

from src.schemas.MixinSchemas import TaskContainerTypes
from src.schemas.TaskContainerSchemas import TaskContainerGet, TaskContainerCreate


class AreaGet(TaskContainerGet):
    type: TaskContainerTypes
    pass


class AreaCreate(TaskContainerCreate):
    # Area only has the default task container fields with type of area
    pass


class AreaUpdate(AreaCreate):
    # Mandatory fields: Id + all the same fields as create operation
    uuid: UUID
