from typing import Annotated
from uuid import UUID

from pydantic import (
    BaseModel as BaseSchemaModel,
    ConfigDict,
    model_validator,
    Field,
)

from app.repository_layer.models.enumerations import RepeatIntervalType
from app.service_layer.schemas.schema_mixins import (
    HasId,
    HasCreatedAndUpdateTimestamps,
    HasOptionalStartAndDeadlineDates,
    HasNameAndOptionalDescription,
    HasTaskOrProjectStatus,
    HasRepeatFields,
)
from app.service_layer.service_exceptions import TasklyServiceValidationError


class TaskBase(BaseSchemaModel, HasRepeatFields):
    project_id: Annotated[
        UUID, Field(description="One of project_id or parent_task_id must be populated")
    ] = None
    parent_task_id: Annotated[
        UUID, Field(description="One of project_id or parent_task_id must be populated")
    ] = None

    @model_validator(mode="after")
    def check_is_subtask_or_has_parent_project(self):
        """DatabaseManager constraint - either parent task or project required"""
        if self.project_id is None and self.parent_task_id is None:
            raise TasklyServiceValidationError(
                "Tasks requires either a project_id or parent_task_id"
            )
        elif self.project_id and self.parent_task_id is None:
            raise TasklyServiceValidationError(
                "Tasks can not have project_id AND parent_task_id"
            )
        return self


class TaskResponse(
    TaskBase,
    HasId,
    HasCreatedAndUpdateTimestamps,
    HasOptionalStartAndDeadlineDates,
    HasNameAndOptionalDescription,
    HasTaskOrProjectStatus,
):
    """Schema returned to API consumers typically via a GET
    request or returned after update a resource"""

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(
    TaskBase,
    HasOptionalStartAndDeadlineDates,
    HasNameAndOptionalDescription,
    HasTaskOrProjectStatus,
):
    """Schema used by API consumers to create a Tasks"""

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(TaskCreate):
    # Same as task create. End points will ask for Id though.

    model_config = ConfigDict(from_attributes=True)


class TaskDelete(BaseSchemaModel):
    pass
