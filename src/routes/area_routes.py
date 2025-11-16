from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.models import TaskContainerTypes
from .. import schemas
from ..core.database import get_database_session
from ..core.router_util import get_task_container_by_id, create_uuid_from_string

area_router = APIRouter()
# Load dependencies
SessionDep = Annotated[Session, Depends(get_database_session)]


# @area_router.get(
# Todo replace based on model in project_routes with service repository
