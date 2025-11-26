from enum import Enum
from typing import Optional, Annotated
from uuid import UUID

from pydantic import (
    ConfigDict,
    AwareDatetime,
    StringConstraints,
    model_validator,
    BaseModel,
    Field,
)

""" Defines common schema elements shared across multiple schema models.
Define in one spot so we do not have to keep multiple in sync. Mix in models
specific to a type e.g. Project are stored under the corresponding schema file"""


class HasId:
    """Schema returned to API consumers typically via a GET
    request or returned after update a resource"""

    model_config = ConfigDict(from_attributes=True)
    id: UUID


class HasParentProjectId:
    "Used for models with foreign key link to group"

    parent_project_id: Optional[UUID] = None


class HasCreatedAndUpdateTimestamps:
    """Schema returned to API consumers typically via a GET
    request or returned after update a resource"""

    model_config = ConfigDict(from_attributes=True)
    created_at: AwareDatetime
    updated_at: AwareDatetime


class HasOptionalStartAndDeadlineDates:
    start_date: Optional[AwareDatetime] = None
    deadline_date: Optional[AwareDatetime] = None


class HasNameAndOptionalDescription:
    name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
    ]
    description: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1)
    ] = None


class TaskAndProjectStatuses(Enum):
    not_started = "Not started"
    in_progress = "Started"
    completed = "Completed"


class HasTaskOrProjectStatus:
    status: TaskAndProjectStatuses = TaskAndProjectStatuses.not_started


class ProjectTypes(Enum):
    """Project types define what fields are allowed.
    Projects - allow all fields including startdate/deadline
    Areas - allows only name and description. These represent areas of focus/life values
    """

    project = "project"
    area = "area"


class HasProjectType:
    type: Annotated[
        ProjectTypes,
        Field(description="See ProjectTypes type description for details"),
    ]
