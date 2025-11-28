from datetime import timedelta
from typing import NamedTuple, Literal, Annotated, Union

from pydantic import (
    AwareDatetime,
    BaseModel as BaseSchemaModel,
    Field,
    StringConstraints,
)
from pydantic_core.core_schema import TimedeltaSchema

from app.repository_layer.models.enumerations import TaskAndProjectStatuses


class DateFilter(BaseSchemaModel):
    field: Literal["created_at", "updated_at", "deadline_date", "start_date"]
    operator: Literal["lt", "le", "gt", "ge", "eq"]
    value: AwareDatetime


class DateFilterRelative(BaseSchemaModel):
    """Date filters relative to today's date e.g. today + 7 days or
    today - 3 days. Only supports addition to today's date"""

    field: Literal["created_at", "updated_at", "deadline_date", "start_date"]
    operator: Literal["lt", "le", "gt", "ge", "eq"]
    timedelta: timedelta


class ParentProjectFilter(BaseSchemaModel):
    """Date filters relative to todays date e.g. today + 7 days or
    today - 3 days. Only supports addition to todays date"""

    project_names: list[
        Annotated[
            str,
            StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
        ],
    ]
    operator: Literal["in", "notIn"]
    include_child_projects: Annotated[
        bool,
        Field(
            default=False,
            description="If true include tasks under any child projects for the searched project name",
        ),
    ]


class DateRangeFilter(BaseSchemaModel):
    field: Literal["created_at", "updated_at", "deadline_date", "start_date"]
    operator: Literal["between"]
    start_date: AwareDatetime
    end_date: AwareDatetime


project_filter_str_value_desc = """Provide string for eq or like operators. Like accepts % for wildcards. For in/not in provide a list of strings"""


class NameFilter(BaseSchemaModel):
    field: Literal["name"]
    operator: Literal["like", "notLike"]
    value: Annotated[
        str, Field(description="Search is case insensitive. Use % for wildcards")
    ]


class NameInSetFilter(BaseSchemaModel):
    field: Literal["name"]
    operator: Literal["in", "notIn"]
    value: Annotated[
        list, Field(description="Provide a list of strings to match against")
    ]


class StatusFilter(BaseSchemaModel):
    field: Literal["status"]
    operator: Literal["in", "notIn"]
    value: list[Literal["Not started", "In Progress", "Completed"]]
