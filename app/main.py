from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware

from app.api.routes.filter_routes import filter_router
from app.api.routes.project_routes import project_router
from app.api.routes.task_routes import task_router
from app.core_layer.config import settings
from app.core_layer.database import create_tables_and_indexes
from app.core_layer.dependency_injector import TasklyDependencyContainer
from app.core_layer.exception_handlers import (
    TasklyBaseException,
    app_specific_exception_handler,
)
from app.service_layer.service_exceptions import TasklyServiceValidationError

app = FastAPI(debug=False)
app.container = TasklyDependencyContainer()
# Generic handler for taskly errors including subclassed exceptions
# Exceptions raised by framework e.g. pydantic validations
app.add_exception_handler(TasklyServiceValidationError, app_specific_exception_handler)
app.add_exception_handler(TasklyBaseException, app_specific_exception_handler)

# Add CORS middleware to set allowed origins
# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add routes
app.include_router(project_router)
app.include_router(task_router)
app.include_router(filter_router)
