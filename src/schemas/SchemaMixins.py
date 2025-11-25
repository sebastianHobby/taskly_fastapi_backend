from enum import Enum
from typing import Optional, Annotated
from uuid import UUID

from pydantic import (
    ConfigDict,
    AwareDatetime,
    StringConstraints,
)


""" Defines common schema elements shared across multiple schema models.
Define in one spot so we do not have to keep multiple in sync. Mix in models
specific to a type e.g. Tasklist are stored under the corresponding schema file"""


class HasId:
    """Schema returned to API consumers typically via a GET
    request or returned after update a resource"""

    model_config = ConfigDict(from_attributes=True)
    id: UUID


class HasGroupId:
    "Used for models with foreign key link to group"

    group_id: UUID


class HasTasklistId:
    "Used for models with foreign key link to task list"

    tasklist_id: UUID


class HasCreatedAndUpdateTimestamps:
    """Schema returned to API consumers typically via a GET
    request or returned after update a resource"""

    model_config = ConfigDict(from_attributes=True)
    created_datetime: AwareDatetime
    updated_datetime: AwareDatetime


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
