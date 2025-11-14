from typing import Annotated
from uuid import UUID
from sqlalchemy.orm import Session

from src import models, schemas
from src.core.database import get_database_session
from fastapi import APIRouter, Depends, status, HTTPException


task_router = APIRouter()
# Load dependencies
SessionDep = Annotated[Session, Depends(get_database_session)]


@task_router.get(
    "/tasks", status_code=status.HTTP_200_OK, response_model=list[schemas.TaskGet]
)
async def get_all_tasks(database: SessionDep):
    tasks_query = database.query(models.Task)
    return tasks_query.all()


@task_router.get(
    "/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=schemas.TaskGet
)
async def get_task_by_id(database: SessionDep, task_id: str):
    try:
        uuid = UUID(task_id)
    except ValueError:
        # Not a valid UUID
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    task = database.query(models.Task).filter(models.Task.id == uuid).first()
    if task is not None:
        return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@task_router.post("/tasks")
async def create_task(database: SessionDep, task_request: schemas.TaskCreate):
    new_task = models.Task(**task_request.model_dump())
    database.add(new_task)
    database.commit()
    database.refresh(new_task)


@task_router.put("/tasks")
async def update_task(
    database: SessionDep, task_request: schemas.TaskUpdate, task_id: str
):
    try:
        uuid = UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    task = database.query(models.Task).filter(models.Task.id == uuid).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    # Update fields based on request object
    for var, value in task_request.model_dump().items():
        setattr(task, var, value) if value is not None else None
    database.commit()
    database.refresh(task)


@task_router.delete("/tasks/{task_id}")
async def delete_task(database: SessionDep, task_id: str):
    try:
        uuid = UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    task = database.query(models.Task).filter(models.Task.id == uuid).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    database.delete(task)
    database.commit()
    database.refresh(task)
