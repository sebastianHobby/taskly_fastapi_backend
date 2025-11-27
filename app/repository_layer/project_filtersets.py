"""Defines filter operations allowed for a given request_data type"""

from typing import Annotated, Literal
from uuid import UUID
from pydantic import BaseModel, Field
from sqlalchemy.sql import operators as sa_op
from sqlalchemy_filterset import (
    AsyncFilterSet,
    Filter,
    LimitOffsetFilter,
    OrderingFilter,
    OrderingField,
)

from app.repository_layer.models.models import Project
from app.repository_layer.task_filterset import (
    BaseTasklyFiltersetRules,
    BaseTasklyFilterParams,
)


class ProjectFiltersetRules(BaseTasklyFiltersetRules):
    """Defines what fields can be filtered on and what operators to use.
    Can be paired with a ProjectFilterParams request_data to define the parameters to be passed
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


class ProjectFilterParams(BaseTasklyFilterParams):
    id: Annotated[UUID, Field(description="The ID of a specific project")] = None
    ids: Annotated[tuple[UUID], Field(description="A list of Ids to return")] = None
    name: Annotated[
        UUID, Field(description="The name of project, case insensitive search")
    ] = None
