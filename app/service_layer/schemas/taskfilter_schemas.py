from typing import Union, Annotated

from pydantic import (
    BaseModel as BaseSchemaModel,
    StringConstraints,
    Field,
    BaseModel,
    Json,
)

from .taskfilter_mixins import (
    DateFilter,
    DateRangeFilter,
    NameFilter,
    NameInSetFilter,
    StatusFilter,
    DateFilterRelative,
    ParentProjectFilter,
)
from .schema_mixins import (
    HasId,
    HasCreatedAndUpdateTimestamps,
)


class FilterRules(BaseModel):
    status: StatusFilter = None
    start_date: Union[DateFilter | DateRangeFilter | DateFilterRelative] = None
    deadline_date: Union[DateFilter | DateRangeFilter | DateFilterRelative] = None
    created_at: Union[DateFilter | DateRangeFilter | DateFilterRelative] = None
    updated_at: Union[DateFilter | DateRangeFilter | DateFilterRelative] = None
    parent_project: ParentProjectFilter = None


class TaskFilterCreate(BaseSchemaModel):
    name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
    ]
    rules: Json[list[FilterRules]]


class TaskFilterUpdate(TaskFilterCreate):
    pass


class TaskFilterResponse(
    TaskFilterCreate,
    HasCreatedAndUpdateTimestamps,
    HasId,
):
    pass
