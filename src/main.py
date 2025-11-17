from contextlib import asynccontextmanager
from fastapi import FastAPI
import fastapi.middleware.cors
from src.schemas import *
from src.core.database import create_database
from src.routes.task_routes import task_router
from src.routes.project_routes import project_router
from src.routes.area_routes import area_router


# This method is called when fast API app object is instantiated and
# returns to function after Yield when shutting down
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre app init code here
    create_database()
    yield
    # Any app shutdown logic here


app = FastAPI(lifespan=lifespan)


# CORS setup
origins = [
    "http://localhost:8081",
    "https://localhost:8081",
]
app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task_router, tags=["tasks"])
app.include_router(area_router, tags=["areas"])
app.include_router(project_router, tags=["projects"])
