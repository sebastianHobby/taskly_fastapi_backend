"""Models defined here as used by 'get_multi' end points to define what
parameters API consumers can pass as path parameters to filter the resource"""

from typing import Annotated

from pydantic import Field, BaseModel, AwareDatetime, ConfigDict

from src.schemas.SchemaMixins import TaskAndProjectStatuses


class HasQueryPaginationParams:
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)


class HasQueryCreatedAndUpdatedParams:
    created_datetime__lt: AwareDatetime = None
    created_datetime__gt: AwareDatetime = None
    created_datetime__eq: AwareDatetime = None
    updated_datetime__lt: AwareDatetime = None
    updated_datetime__gt: AwareDatetime = None
    updated_datetime__eq: AwareDatetime = None


class HasQueryTaskOrProjectStatus:
    status_eq: TaskAndProjectStatuses = None


class HasQueryParamStartAndDeadlineDates:
    start_date__lt: AwareDatetime = None
    start_date__gt: AwareDatetime = None
    start_date__eq: AwareDatetime = None
    deadline_date__lt: AwareDatetime = None
    deadline_date__gt: AwareDatetime = None
    deadline_date__eq: AwareDatetime = None


class HasQueryNameAndDescription:
    name__match: Annotated[
        str,
        Field(
            max_length=100,
            description="Full text search including stemming e.g. 'speaking' will match 'speak'",
        ),
    ] = None
    description__match: Annotated[
        str,
        Field(
            description="Full text search including stemming e.g. 'speaking' will match 'speak'"
        ),
    ] = None


class GroupQueryParams(
    BaseModel,
    HasQueryPaginationParams,
    HasQueryNameAndDescription,
    HasQueryCreatedAndUpdatedParams,
):
    model_config = ConfigDict(extra="forbid")
    pass


class TasklistQueryParams(
    BaseModel,
    HasQueryPaginationParams,
    HasQueryParamStartAndDeadlineDates,
    HasQueryNameAndDescription,
    HasQueryTaskOrProjectStatus,
    HasQueryCreatedAndUpdatedParams,
):
    model_config = ConfigDict(extra="forbid")
    pass


class TaskQueryParams(
    BaseModel,
    HasQueryPaginationParams,
    HasQueryParamStartAndDeadlineDates,
    HasQueryNameAndDescription,
    HasQueryTaskOrProjectStatus,
    HasQueryCreatedAndUpdatedParams,
):
    model_config = ConfigDict(extra="forbid")
    pass
