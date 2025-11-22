from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import ConfigDict

from pydantic import BaseModel as BaseSchemaModel

from src.models.db_models import ListGroup
from src.schemas.ListGroupSchemas import ListGroupResponse
from src.schemas.TaskListSchemas import TaskListResponse
from src.schemas.TaskSchemas import TaskResponse


class TaskListAndListGroups(BaseSchemaModel):
    ListGroup: List[ListGroupResponse]
    TaskList: List[TaskListResponse]


class TaskListWithTaskResponse(BaseSchemaModel):
    TaskList: TaskListResponse
    Tasks: List[TaskResponse]
