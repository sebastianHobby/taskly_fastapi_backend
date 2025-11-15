import copy
import os
import uuid
from datetime import datetime
import json
from typing import Literal

import pytest
from pytest import Metafunc
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from src.core.database import get_database_session, Base
from src.main import app
from src.models import *
from src.routes.task_routes import task_router
from src.schemas import *


@pytest.fixture(name="session_fixture", scope="function")
def session_fixture():
    # Create in memory database for testing
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.drop_all(bind=engine)  # Drop data from any previous test runs
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client_fixture", scope="function")
def client_fixture(session_fixture: Session):
    def get_session_override():
        return session_fixture

    # Override database dependency to point to test database just for duration of test
    app.dependency_overrides[get_database_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def validate_schema_is_subset_of_database_model(
    db_model: Base, schema_model: BaseModel
) -> None:
    """Generic method to compare pydantic model (schema) against SQL alchemy database model.
    We expect the database model to be a superset of the any pydantic schema. Pydantic schemas
    represent the data we use as inputs/outputs for our API and often do not include all data
    in database"""
    schema_as_dict = schema_model.model_dump()
    for schema_key, schema_value in schema_as_dict.items():
        # comparison = f"Checking database has {schema_key} with value {schema_value}"
        # print(comparison)
        assert (
            getattr(db_model, schema_key) == schema_value
        )  # Assert db model has field with same name and value as schema
    # for var, value in project_request.model_dump().items():
    #     setattr(project, var, value) if value is not None else None


class TestProjectsWithScenarios:

    project_mandatory_fields_only_dict = {
        "description": "description",
        "name": "Mandatory fields only",
        "is_complete": True,
    }
    project_all_fields_except_parent_dict = {
        "description": "description",
        "name": "All fields except parent",
        "is_complete": True,
        "start_date": (datetime.today() - timedelta(weeks=4)),
        "deadline_date": (datetime.today() + timedelta(weeks=4)),
        "last_reviewed_date": (datetime.today() + timedelta(weeks=4)),
    }

    areaUUID = UUID
    area_all_fields_dict = {
        "description": "area all fields",
        "name": "area fields only",
        "last_reviewed_date": (datetime.today()),
    }

    @pytest.mark.parametrize(
        "db_project_dict,create_parent_area",
        [
            (project_all_fields_except_parent_dict, False),
            (project_all_fields_except_parent_dict, True),
        ],
        ids=[
            "single project all fields except parent",
            "single project all fields with parent",
        ],
    )
    def test_project_get(
        self,
        client_fixture: TestClient,
        session_fixture: Session,
        db_project_dict: dict,
        create_parent_area: bool,
    ):
        # Set up data in our temp test DB
        parent_area = None
        if create_parent_area:
            parent_area = Area(
                name="parent area", description="parent_area description"
            )
            session_fixture.add(parent_area)
            session_fixture.commit()

        if db_project_dict:
            db_project = Project(**db_project_dict)
            if parent_area:
                db_project.parent_area = parent_area
            session_fixture.add(db_project)
            session_fixture.commit()

        response = client_fixture.get(f"/projects/{db_project.id}")
        assert response.status_code == 200

        # Load into schema model for initial type validations
        schema_project = ProjectGet.model_validate(response.json())
        # Check any values in schema have matching field in database object. Note DB object is superset (i.e. has extra data)
        validate_schema_is_subset_of_database_model(
            db_model=db_project, schema_model=schema_project
        )

    def test_project_get_invalid_id(self, client_fixture: TestClient):
        response = client_fixture.get(f"/projects/123")
        assert response.status_code == 404

    #
    @pytest.mark.parametrize(
        "db_projects_dict,create_parent_area",
        [
            (
                [
                    project_mandatory_fields_only_dict,
                    project_all_fields_except_parent_dict,
                ],
                False,
            ),
            ([], False),
            (
                [
                    project_mandatory_fields_only_dict,
                    project_all_fields_except_parent_dict,
                ],
                True,
            ),
        ],
        ids=[
            "Multiples project no parent",
            "No data",
            "Multiples project with PARENT ",
        ],
    )
    def test_get_invalid_project_id(clientFixture: TestClient, sessionFixture: Session):
        response = clientFixture.get(f"/projects/123")
        assert response.status_code == 404

    def test_projects_get_all(
        self,
        client_fixture: TestClient,
        session_fixture: Session,
        db_projects_dict: dict,
        create_parent_area: bool,
    ):
        db_areas = []
        db_projects = []
        parent_area = None
        if create_parent_area:
            parent_area = Area(
                name="parent area", description="parent_area description"
            )
            session_fixture.add(parent_area)
            session_fixture.commit()

        if db_projects_dict and len(db_projects_dict):
            db_projects = [Project(**x) for x in db_projects_dict]
            if parent_area:
                for project in db_projects:
                    project.parent_id = parent_area.id
            session_fixture.add_all(db_projects)

        response = client_fixture.get("/projects/")
        assert response.status_code == 200
        data = response.json()

        schema_models = []
        for line in data:
            schema_models.append(ProjectGet.model_validate(line))

        for db_project in db_projects:
            matching_schema_found = False
            # session_fixture.refresh(db_project)
            for schema in schema_models:
                if schema.id == db_project.id:
                    matching_schema_found = True
                    validate_schema_is_subset_of_database_model(
                        db_model=db_project, schema_model=schema
                    )
            assert matching_schema_found == True

    # Load response JSON into schema (pydantic model)ProjectGet

    @pytest.mark.parametrize(
        "db_project_dict,create_parent_area",
        [
            (project_all_fields_except_parent_dict, False),
            (project_all_fields_except_parent_dict, True),
            (project_mandatory_fields_only_dict, True),
            (project_mandatory_fields_only_dict, False),
        ],
        ids=[
            "single project all fields without parent "
            "single project all fields with parent",
            "single project mandatory fields only with parent",
            "single project mandatory fields only without parent",
        ],
    )
    # def test_project_create(
    #     client_fixture: TestClient, db_project_dict: dict, create_parent_area: bool
    # ):
    #     # Todo fix me
    #     response = client_fixture.post(
    #         "/projects/",
    #         json={
    #             "name": "My test project",
    #             "description": "Created by My test project",
    #             "is_complete": "true",
    #         },
    #     )
    #     # Validate response
    #     data = response.json()
    #     assert response.status_code == 200
    #     assert data["name"] == "My test project"
    #     assert data["id"] is not None
    #     assert data["description"] == "Created by My test project"
    #     assert data["is_complete"] == True


# #
# # def test_create_area(clientFixture: TestClient, sessionFixture: Session):
# #     # Create area object
# #     response = clientFixture.post("/areas/", json={"name": "My area"})
# #     # Validate response
# #     data = response.json()
# #     assert response.status_code == 200
# #     assert data["name"] == "My area"
#     uuid_string = data["id"]
#     uuidObj = uuid.UUID(uuid_string, version=4)
#     assert uuidObj is not None
#
#
# def test_create_project_with_area(clientFixture: TestClient, sessionFixture: Session):
#     # Create area object
#     area_1 = models.Area(name="My test area")
#     sessionFixture.add(area_1)
#     sessionFixture.commit()
#
#     # Now try to use POST API call to create project linked to area
#     uuid_string = str(area_1.id)
#     response = clientFixture.post(
#         "/projects/",
#         json={
#             "name": "My test project",
#             "description": "Created by My test project",
#             "is_complete": "true",
#             "area_id": uuid_string,
#         },
#     )
#
#     # Validate response
#     data = response.json()
#     assert response.status_code == 200
#     assert data["name"] == "My test project"
#     assert data["id"] is not None
#     assert data["description"] == "Created by My test project"
#     assert data["is_complete"] == True
#
#     uuid_string = data["area_id"]
#
#
# #  print(type(uuid_string))
# #  uuidObj = uuid.UUID(uuid_string, version=4)
# #  assert uuidObj == area_1.id
#
#
# def test_get_projects(clientFixture: TestClient, sessionFixture: Session):
#     project_1 = models.Project(
#         name="My test project",
#         description="Created by My test project",
#         is_complete=False,
#         id=uuid.uuid4(),
#         area_id=None,
#         createdAt=datetime.now(),
#         updatedAt=datetime.now(),
#     )
#     sessionFixture.add(project_1)
#
#     area_1 = models.Area(name="My first area", id=uuid.uuid4())
#
#     project_2 = models.Project(
#         name="My second project",
#         description="2nd description",
#         is_complete=True,
#         id=uuid.uuid4(),
#         area_id=area_1.id,
#         createdAt=datetime.now(),
#         updatedAt=datetime.now(),
#     )
#
#     sessionFixture.add(project_1)
#     sessionFixture.add(project_2)
#     sessionFixture.add(area_1)
#
#     sessionFixture.commit()
#     response = clientFixture.get("/projects/")
#     # Validate response
#     data = response.json()
#     assert response.status_code == 200
#     assert data[0]["name"] == "My test project"
#     assert data[0]["description"] == "Created by My test project"
#     assert data[0]["is_complete"] == False
#     assert data[0]["area_id"] is None
#     assert data[0]["id"] is not None
#     assert data[0]["createdAt"] is not None
#     assert data[0]["updatedAt"] is not None
#
#     assert data[1]["name"] == "My second project"
#     assert data[1]["createdAt"] is not None
#     assert data[1]["updatedAt"] is not None
#     assert data[1]["id"] is not None
#     assert data[1]["description"] == "2nd description"
#     assert data[1]["is_complete"] == True
#     assert data[1]["area_id"] is not None
#
#
# def test_get_areas(clientFixture: TestClient, sessionFixture: Session):
#     project_1 = models.Project(
#         name="My test project",
#         description="Created by My test project",
#         is_complete=False,
#         id=uuid.uuid4(),
#         area_id=None,
#         createdAt=datetime.now(),
#         updatedAt=datetime.now(),
#     )
#     sessionFixture.add(project_1)
#
#     area_1 = models.Area(name="My first area", id=uuid.uuid4())
#
#     project_2 = models.Project(
#         name="My second project",
#         description="2nd description",
#         is_complete=True,
#         id=uuid.uuid4(),
#         area_id=area_1.id,
#         createdAt=datetime.now(),
#         updatedAt=datetime.now(),
#     )
#
#     sessionFixture.add(project_1)
#     sessionFixture.add(project_2)
#     sessionFixture.add(area_1)
#
#     sessionFixture.commit()
#     response = clientFixture.get("/projects/")
#     # Validate response
#     data = response.json()
#     assert response.status_code == 200
#     assert data[0]["name"] == "My test project"
#     assert data[0]["description"] == "Created by My test project"
#     assert data[0]["is_complete"] == False
#     assert data[0]["area_id"] is None
#     assert data[0]["id"] is not None
#     assert data[0]["createdAt"] is not None
#     assert data[0]["updatedAt"] is not None
#
#     assert data[1]["name"] == "My second project"
#     assert data[1]["createdAt"] is not None
#     assert data[1]["updatedAt"] is not None
#     assert data[1]["id"] is not None
#     assert data[1]["description"] == "2nd description"
#     assert data[1]["is_complete"] == True
#     assert data[1]["area_id"] is not None
