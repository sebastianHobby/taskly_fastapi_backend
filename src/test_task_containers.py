import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from src.core.database import get_database_session
from src.main import app
from src.models.AreaModel import Area
from src.models.ProjectModel import Project
from src.schemas.ProjectSchemas import ProjectGet, ProjectCreate
from src.schemas.MixinSchemas import *
from src.schemas.MixinSchemas import TaskContainerTypes


# Todo expand tests to cover all routes


@pytest.fixture(name="session_fixture", scope="function", autouse=True)
def session_fixture():
    # Create in memory database for testing
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLAlchemyBase.metadata.drop_all(
        bind=engine
    )  # Drop data from any previous test runs
    SQLAlchemyBase.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client_fixture", scope="function", autouse=True)
def client_fixture(session_fixture: Session):
    def get_session_override():
        return session_fixture

    # Override database dependency to point to test database just for duration of test
    app.dependency_overrides[get_database_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def validate_schema_is_subset_of_database_model(
    db_model: SQLAlchemyBase, schema_model: ApiBaseSchema
) -> None:
    """Generic method to compare pydantic model (schema) against SQL alchemy database model.
    We expect the database model to be a superset of the any pydantic schema. Pydantic schemas
    represent the data we use as inputs/outputs for our API and often do not include all data
    in database"""
    schema_as_dict = schema_model.model_dump()
    for schema_key, schema_value in schema_as_dict.items():
        # comparison = f"Checking database has {schema_key} with value {schema_value}"
        # print(comparison)
        assert getattr(db_model, schema_key) == schema_value
        # Assert db model has field with same name and value as schema
    # for var, value in project_request.model_dump().items():
    #     setattr(project, var, value) if value is not None else None


class TestProjects:
    def test_get_invalid_id(self, client_fixture, session_fixture):
        response = client_fixture.get(f"/projects/123")
        assert response.status_code == 404

    def test_get_by_id(self, session_fixture, client_fixture):
        # Setup test data
        db_project = Project(
            name="my test project",
            description="my test project",
            start_date=datetime.now(),
            deadline_date=(datetime.now() + timedelta(weeks=3)),
            type=TaskContainerTypes.project,
        )
        session_fixture.add(db_project)
        session_fixture.commit()

        response = client_fixture.get(f"/projects/{db_project.id}")
        data = response.json()
        assert response.status_code == 200

        # Confirm the data returned in schema matches the corresponding fields in database
        schema = ProjectGet.model_validate(data)
        validate_schema_is_subset_of_database_model(
            db_model=db_project, schema_model=schema
        )

    def test_get_all(self, session_fixture, client_fixture):
        # Setup test data
        db_projects = []
        schemas = []
        db_project_all_fields = Project(
            name="my test project",
            description="my test project",
            start_date=datetime.now(),
            deadline_date=(datetime.now() + timedelta(weeks=3)),
            type=TaskContainerTypes.project,
        )
        session_fixture.add(db_project_all_fields)
        db_projects.append(db_project_all_fields)

        db_project_mand_fields_only = Project(
            name="my test project",
            description="my test project",
            type=TaskContainerTypes.project,
        )
        session_fixture.add(db_project_mand_fields_only)
        db_projects.append(db_project_mand_fields_only)

        db_area = Area(name="my test area", description="my test area description")
        session_fixture.add(db_area)

        db_project_with_parent_area = Project(
            name="my test project",
            description="my test project",
            start_date=datetime.now(),
            deadline_date=(datetime.now() + timedelta(weeks=3)),
            type=TaskContainerTypes.project,
            parent_id=db_area.id,
        )

        session_fixture.add(db_project_with_parent_area)
        db_projects.append(db_project_with_parent_area)

        session_fixture.commit()

        response = client_fixture.get(f"/projects")
        data = response.json()
        assert response.status_code == 200

        for line in data:
            schemas.append(ProjectGet.model_validate(line))

        # Confirm the data returned in schema matches the corresponding fields in database
        for db_project in db_projects:
            match_found = False
            for schema_model in schemas:
                if db_project.id == schema_model.id:
                    match_found = True
                    validate_schema_is_subset_of_database_model(
                        db_model=db_project, schema_model=schema_model
                    )
            assert match_found

    def test_create_project(self, client_fixture, session_fixture):
        # Create area as parent
        db_area = Area(name="my test area", description="my test area description")
        session_fixture.add(db_area)
        session_fixture.commit()

        # First test insert with mandatory fields only
        request_json = {
            "name": "My test project",
            "description": "Created by My test project",
        }
        response = client_fixture.post("/projects/", json=request_json)
        assert response.status_code == 200
        responseSchema = ProjectGet.model_validate(response.json())
        db_project_load = session_fixture.get(Project, responseSchema.id)

        # Compare the object returned by POST against database
        validate_schema_is_subset_of_database_model(
            db_model=db_project_load, schema_model=responseSchema
        )
        # Compare project create schema based on our reguest against database values
        projectCreateSchema = ProjectCreate(**request_json)
        validate_schema_is_subset_of_database_model(
            db_model=db_project_load, schema_model=projectCreateSchema
        )


# Todo finish project test cases , area test cases and task

#     )
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
