from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.database import create_database_and_tables
from src.routes.task_routes import task_router
from src.routes.project_routes import project_router
from src.routes.area_routes import area_router

# Create required tables
create_database_and_tables()
# TODO fix link project to GIT for soruce control before you lose it somehow

app = FastAPI()
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

# @app.on_event("startup")
# def on_startup():
