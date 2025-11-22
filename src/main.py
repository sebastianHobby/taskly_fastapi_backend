from contextlib import asynccontextmanager
from typing import Annotated

import fastapi.middleware.cors
from dependency_injector.ext.starlette import Lifespan
from dependency_injector.wiring import inject, Provide
from fastapi import FastAPI

from src.core.dependency_containers import Container
from src.routes.list_group_routes import list_group_router
from src.routes.task_list_routes import task_lists_router
from src.routes.task_routes import task_router
from src.services import task_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup events: Initialize resources here
    print("Application startup: Initializing database connection...")
    database = Container.database()
    database.create_database()
    yield
    # Shutdown events: Clean up resources here
    print("Application shutdown: Closing database connection...")
    await database.shutdown()


def create_app() -> FastAPI:
    container = Container()
    database = container.database()
    database.create_database()
    app = FastAPI(lifespan=lifespan, debug=container.config.debug)
    app.container = container
    app.include_router(task_lists_router)
    app.include_router(list_group_router)
    app.include_router(task_router)
    # app.include_router(task_router, tags=["tasks"])
    # app.include_router(area_router, tags=["areas"])

    app.add_middleware(
        fastapi.middleware.cors.CORSMiddleware,
        allow_origins=container.config.cors.allow_origins(),
        allow_credentials=container.config.cors.allow_credentials(),
        allow_methods=container.config.cors.allow_methods(),
        allow_headers=container.config.cors.allow_headers(),
    )

    return app


app = create_app()
