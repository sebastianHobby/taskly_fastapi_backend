from typing import Literal, Union, Annotated, NamedTuple

from pydantic import BaseModel as BaseSchemaModel, NaiveDatetime, Field, AwareDatetime

from app.repository_layer.models.enumerations import TaskAndProjectStatuses
from .schema_mixins import (
    HasId,
    HasNameAndOptionalDescription,
    HasCreatedAndUpdateTimestamps,
)


class DateRange(NamedTuple):
    start_date: AwareDatetime
    end_date: AwareDatetime


class ProjectFilterDateRules(BaseSchemaModel):
    field: Literal["created_at", "updated_at", "deadline_date", "start_date"]
    operator: Literal["lt", "gt", "eq", "between"]
    value: Annotated[
        Union[AwareDatetime, DateRange],
        Field(
            description="Provide Daterange for between operations. For all others provide single Datetime"
        ),
    ]


project_filter_str_value_desc = """Provide string for eq or like operators. Like accepts % for wildcards. For in/not in provide a list of strings"""


class ProjectFilterStrRules(BaseSchemaModel):
    field: Literal["name"]
    operator: Literal["eq", "like", "in", "notIn"]
    value: Annotated[
        Union[str | list[str]], Field(description=project_filter_str_value_desc)
    ]


class ProjectFilterEnumRules(BaseSchemaModel):
    field: Literal["status"]
    operator: Literal["in", "notIn"]
    value: list[TaskAndProjectStatuses]


class TaskFilterDateRules(BaseSchemaModel):
    field: Literal["created_at", "updated_at", "deadline_date", "start_date"]
    operator: Literal["lt", "gt", "eq", "between"]
    value: Annotated[
        Union[AwareDatetime, DateRange],
        Field(
            description="Provide Daterange for between operations. For all others provide single Datetime"
        ),
    ]


task_filter_str_value_desc = """Provide string for eq or like operators. Like accepts % for wildcards. For in/not in provide a list of strings"""


class TaskFilterStrRules(BaseSchemaModel):
    field: Literal["name"]
    operator: Literal["eq", "like", "in", "notIn"]
    value: Annotated[
        Union[str | list[str]], Field(description=task_filter_str_value_desc)
    ]


class TaskFilterEnumRules(BaseSchemaModel):
    field: Literal["status"]
    operator: Literal["in", "notIn"]
    value: list[TaskAndProjectStatuses]


class FilterResponse(
    BaseSchemaModel, HasCreatedAndUpdateTimestamps, HasId, HasNameAndOptionalDescription
):

    project_filter_rules: list[
        Union[ProjectFilterDateRules, ProjectFilterStrRules, ProjectFilterEnumRules]
    ] = None
    task_filter_rules: list[
        Union[TaskFilterDateRules, TaskFilterStrRules, TaskFilterEnumRules]
    ] = None


class FilterCreate(BaseSchemaModel, HasNameAndOptionalDescription):

    project_filter_rules: list[
        Union[ProjectFilterDateRules, ProjectFilterStrRules, ProjectFilterEnumRules]
    ] = None
    task_filter_rules: list[
        Union[TaskFilterDateRules, TaskFilterStrRules, TaskFilterEnumRules]
    ] = None


class FilterUpdate(FilterCreate):
    pass
