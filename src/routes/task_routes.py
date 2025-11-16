from typing import Annotated
from uuid import UUID
from sqlalchemy.orm import Session

from src import models, schemas
from src.core.database import get_database_session
from fastapi import APIRouter, Depends, status, HTTPException


task_router = APIRouter()
# Load dependencies
SessionDep = Annotated[Session, Depends(get_database_session)]


# @area_router.get(
# Todo replace based on model in project_routes with service repository
# Todo move session instantiation into the service repository layer
