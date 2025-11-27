"""Defines filter operations allowed for a given request_data type"""

from typing import Annotated

import sqlalchemy_filterset
from pydantic import BaseModel, Field


class BaseTasklyFiltersetRules(sqlalchemy_filterset.AsyncFilterSet):
    pagination = sqlalchemy_filterset.LimitOffsetFilter()


class BaseTasklyFilterParams(BaseModel):
    page: int = Field(
        gt=0,
        le=200,
        description="The number of resources returned per page",
        default=1,
    )
    itemsPerPage: int = Field(
        gt=0, description="The number of resources returned per page", default=100
    )
