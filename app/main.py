from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware

from app.api.routes.project_routes import project_router
from app.api.routes.task_routes import task_router
from app.core_layer.config import settings
from app.core_layer.dependency_injector import TasklyDependencyContainer
from app.core_layer.exception_handlers import (
    app_exception_handler,
    http_exception_handler,
    TasklyBaseException,
    generic_exception_handler,
    validation_exception_handler,
)

app = FastAPI(debug=False)
app.container = TasklyDependencyContainer()
# Generic handler for taskly errors including subclassed exceptions
app.add_exception_handler(TasklyBaseException, app_exception_handler)
# Exceptions raised by framework e.g. pydantic validations
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# General uncaught exceptions - for the unknown.
app.add_exception_handler(Exception, generic_exception_handler)

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
