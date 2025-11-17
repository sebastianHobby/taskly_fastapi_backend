from src.models.TaskContainerModel import TaskContainer
from src.schemas.MixinSchemas import TaskContainerTypes


class Area(TaskContainer):
    # Tell SQL alchemy to refer to this table when task_container.type = project
    __mapper_args__ = {"polymorphic_identity": TaskContainerTypes.area}
