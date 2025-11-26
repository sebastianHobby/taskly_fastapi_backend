import datetime
from contextlib import asynccontextmanager

import fastapi.middleware.cors
from dependency_injector.wiring import Provide
from fastapi import FastAPI

from src.core.DependencyContainers import Container
from src.core.ExceptionHandlers import init_exception_handlers
from src.routes.project_routes import project_router
from src.routes.task_routes import task_router


@asynccontextmanager
async def lifespan(fast_api_app: FastAPI):
    # Startup events: Initialize resources here
    print("Application startup: Initializing database_manager connection...")

    fast_api_app.container = Container()
    database = fast_api_app.container.database_manager()
    await database.create_tables_and_indexes()
    print("Application startup: Adding exception handlers...")
    print("Application startup: Adding routes...")
    fast_api_app.include_router(project_router)
    fast_api_app.include_router(task_router)

    yield
    # Shutdown events: Clean up resources here
    print("Application shutdown: Closing database_manager connection...")
    await database.shutdown()


app = FastAPI(lifespan=lifespan, debug=False)
app.container = Container()
init_exception_handlers(app=app)

# Note below can not be moved into lifespan handler or errors with can not add middleware
# after APP startup
app.add_middleware(fastapi.middleware.cors.CORSMiddleware, **Container.config.cors())
