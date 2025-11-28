from datetime import timedelta
from typing import Optional, Annotated
from uuid import UUID

from pydantic import (
    ConfigDict,
    AwareDatetime,
    StringConstraints,
    Field,
    model_validator,
    BaseModel,
)

from app.repository_layer.models.enumerations import (
    ProjectTypes,
    TaskAndProjectStatuses,
    RepeatIntervalType,
)
from app.service_layer.service_exceptions import (
    TasklyServiceException,
    TasklyServiceValidationError,
)

""" Defines common schema elements shared across multiple schema models.
Define in one spot so we do not have to keep multiple in sync. Mix in models
specific to a type e.g. Projects are stored under the corresponding schema file"""


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


class HasRepeatFields:
    model_config = ConfigDict(from_attributes=True)
    repeat_interval_type: RepeatIntervalType = None
    repeat_interval: timedelta = None
    repeat_start: AwareDatetime = None
    repeat_end: AwareDatetime = None

    @model_validator(mode="after")
    def check_repeating_dates(self):
        """DatabaseManager constraint - either parent task or project required"""
        if (
            self.repeat_interval_type is None
            or self.repeat_interval_type is RepeatIntervalType.no_repeat
        ):
            if (
                self.repeat_start is not None
                or self.repeat_end is not None
                or self.repeat_interval is not None
            ):
                raise TasklyServiceValidationError(
                    f"Repeat start date,end date and interval must not be set for repeat type {RepeatIntervalType.no_repeat}"
                )
        elif self.repeat_interval_type is RepeatIntervalType.from_repeat_start_date:
            if self.repeat_start is None or self.repeat_interval is None:
                raise TasklyServiceValidationError(
                    f"Repeat start date and interval required for repeat type {RepeatIntervalType.from_repeat_start_date}"
                )
        elif self.repeat_interval_type is RepeatIntervalType.from_last_completed_date:
            if self.repeat_interval is None:
                raise TasklyServiceValidationError(
                    f"Repeat interval required for repeat type {RepeatIntervalType.from_last_completed_date}"
                )
            if self.repeat_start is not None:
                raise TasklyServiceValidationError(
                    f"Repeat start date must not be sent for {RepeatIntervalType.from_last_completed_date}"
                )


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


class HasTaskOrProjectStatus:
    status: TaskAndProjectStatuses = TaskAndProjectStatuses.not_started


class HasProjectType:
    type: Annotated[
        ProjectTypes,
        Field(description="See ProjectTypes type description for details"),
    ]
