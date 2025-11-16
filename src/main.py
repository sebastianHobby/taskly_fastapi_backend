import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.database import create_database_and_tables

from src.models import *
from src.routes.task_routes import task_router
from src.routes.project_routes import project_router
from src.routes.area_routes import area_router

# Create required tables
# create_database_and_tables()
# asyncio.run(create_database_and_tables())

app = FastAPI()


@app.on_event("startup")
def initialize_startup():
    create_database_and_tables()


# CORS setup
origins = [
    "http://localhost:8081",
    "https://localhost:8081",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task_router, tags=["tasks"])
app.include_router(area_router, tags=["areas"])
app.include_router(project_router, tags=["projects"])
