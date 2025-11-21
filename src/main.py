from contextlib import asynccontextmanager
from typing import Annotated

import fastapi.middleware.cors
from dependency_injector.ext.starlette import Lifespan
from dependency_injector.wiring import inject, Provide
from fastapi import FastAPI

from src.core.dependency_containers import Container
from src.models.db_models import DatabaseBaseModel
from src.routes.area_routes import area_router
from src.routes.project_routes import project_router
from src.routes.task_routes import task_router


def create_app() -> FastAPI:
    container = Container()
    database = container.database()
    database.create_database()
    app = FastAPI()
    app.container = container
    app.include_router(project_router, tags=["projects"])
    app.include_router(task_router, tags=["tasks"])
    app.include_router(area_router, tags=["areas"])

    app.add_middleware(
        fastapi.middleware.cors.CORSMiddleware,
        allow_origins=container.config.cors.allow_origins(),
        allow_credentials=container.config.cors.allow_credentials(),
        allow_methods=container.config.cors.allow_methods(),
        allow_headers=container.config.cors.allow_headers(),
    )

    return app


app = create_app()
