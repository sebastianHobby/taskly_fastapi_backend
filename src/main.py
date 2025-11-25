import datetime
from contextlib import asynccontextmanager

import fastapi.middleware.cors
from dependency_injector.wiring import Provide
from fastapi import FastAPI

from src.core.DependencyContainers import Container
from src.core.ExceptionHandlers import init_exception_handlers
from src.routes.GroupRoutes import group_router
from src.routes.TaskListRoutes import tasklist_router
from src.routes.TaskRoutes import task_router


@asynccontextmanager
async def lifespan(fast_api_app: FastAPI):
    # Startup events: Initialize resources here
    print("Application startup: Initializing database connection...")

    fast_api_app.container = Container()
    database = fast_api_app.container.database()
    await database.create_tables_and_indexes()
    print("Application startup: Adding exception handlers...")
    init_exception_handlers(app=fast_api_app)
    print("Application startup: Adding routes...")
    fast_api_app.include_router(group_router)
    fast_api_app.include_router(tasklist_router)
    fast_api_app.include_router(task_router)

    yield
    # Shutdown events: Clean up resources here
    print("Application shutdown: Closing database connection...")
    await database.shutdown()


app = FastAPI(lifespan=lifespan, debug=False)


# Note below can not be moved into lifespan handler or errors with can not add middleware
# after APP startup
app.add_middleware(fastapi.middleware.cors.CORSMiddleware, **Container.config.cors())
