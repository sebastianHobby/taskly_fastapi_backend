from typing import Annotated, NamedTuple
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy_filterset import (
    Filter,
    RangeFilter,
    BooleanFilter,
    LimitOffsetFilter,
    OrderingFilter,
    OrderingField,
    FilterSet,
    AsyncFilterSet,
)
from sqlalchemy.sql import operators as sa_op
from ..models.project_model import Project

# See doco at https://sqlalchemy-filterset.github.io/sqlalchemy-filterset/filters/#custom-filter


class ProjectFilterSet(AsyncFilterSet):
    """Defines what fields can be filtered on and what operators to use.
    Can be paired with a ProjectFilterParams object to define the parameters to be passed
    in to GET operation in endpoint. Names have to match for automatic translation
    between the models"""

    id = Filter(Project.id, lookup_expr=sa_op.eq)
    ids = Filter(Project.id, lookup_expr=sa_op.eq)
    name = Filter(Project.name, lookup_expr=sa_op.ilike_op)

    pagination = LimitOffsetFilter()
    # Defines what fields can be used to order the search
    ordering = OrderingFilter(
        name=OrderingField(Project.name),
        start_date=OrderingField(Project.start_date),
        created_at=OrderingField(Project.created_at),
    )


class ProjectFilterParams(BaseModel):
    id: Annotated[UUID, Field(description="The ID of a specific project")] = None
    ids: Annotated[tuple[UUID], Field(description="A list of Ids to return")] = None
    name: Annotated[
        UUID, Field(description="The name of project, case insensitive search")
    ] = None
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)

    @property
    def limit_offset(self) -> tuple[int | None, int | None] | None:
        if self.limit or self.offset:
            return self.limit, self.offset
        return None
