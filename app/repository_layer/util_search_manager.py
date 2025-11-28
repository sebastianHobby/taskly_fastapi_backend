"""Defines filter operations allowed for a given request_data type"""

from sqlalchemy.sql import operators as sa_op
from sqlalchemy_filterset import (
    Filter,
    LimitOffsetFilter,
    OrderingFilter,
    OrderingField,
    AsyncFilterSet,
    InFilter,
)

from app.repository_layer.models.models import Projects


class RepositoryCommonSearchFieldManager(AsyncFilterSet):
    """Used to perform searches on common fields shared by all entities"""

    id = Filter(Projects.id, lookup_expr=sa_op.eq)
    ids = InFilter(Projects.id)
    name = Filter(Projects.name, lookup_expr=sa_op.ilike_op)
    pagination = LimitOffsetFilter()
    ordering = OrderingFilter(
        name=OrderingField(Projects.name),
        created_at=OrderingField(Projects.created_at),
        updated_at=OrderingField(Projects.updated_at),
    )
