import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from ..core.database import get_database_session, Base
from ..main import app


# Pytest fixtures work by setting a name for each fixture
# Any methods defined after these that pass in a variable
# with exact same name will have the return value of fixture
# Injected e.g.
# @pytest.fixture(name="nameFixture")
# def get_name
#   return 'bob'
# The nameFixture variable below will be set to return value of get_name
# def my_test_case(nameFixture: Str)
# ...

# TODO automate the test run for this on save? Or deploy ? On commit to git hub?
# Todo complete unit tests - check this with IDE coverage tool does not need 100%
# but interesting to see


@pytest.fixture(name="sessionFixture")
def session_fixture():
    # Create in memory database for testing
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="clientFixture")
def client_fixture(sessionFixture: Session):
    def get_session_override():
        print("Overriding database to use TEST - get_session_override()")
        return sessionFixture

    # Override database dependency to point to test database just for duration of test
    app.dependency_overrides[get_database_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# Test create cases for project and area
def test_create_project(clientFixture: TestClient):
    response = clientFixture.post(
        "/projects/",
        json={
            "name": "My test project",
            "description": "Created by My test project",
            "is_complete": "true",
        },
    )
    # Validate response
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "My test project"
    assert data["id"] is not None
    assert data["description"] == "Created by My test project"
    assert data["is_complete"] == True


def test_create_area(clientFixture: TestClient, sessionFixture: Session):
    # Create area object
    response = clientFixture.post("/areas/", json={"name": "My area"})
    # Validate response
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "My area"
    uuid_string = data["id"]
    uuidObj = uuid.UUID(uuid_string, version=4)
    assert uuidObj is not None


def test_create_project_with_area(clientFixture: TestClient, sessionFixture: Session):
    # Create area object
    area_1 = models.Area(name="My test area")
    sessionFixture.add(area_1)
    sessionFixture.commit()

    # Now try to use POST API call to create project linked to area
    uuid_string = str(area_1.id)
    response = clientFixture.post(
        "/projects/",
        json={
            "name": "My test project",
            "description": "Created by My test project",
            "is_complete": "true",
            "area_id": uuid_string,
        },
    )

    # Validate response
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "My test project"
    assert data["id"] is not None
    assert data["description"] == "Created by My test project"
    assert data["is_complete"] == True

    uuid_string = data["area_id"]


#  print(type(uuid_string))
#  uuidObj = uuid.UUID(uuid_string, version=4)
#  assert uuidObj == area_1.id


def test_get_projects(clientFixture: TestClient, sessionFixture: Session):
    project_1 = models.Project(
        name="My test project",
        description="Created by My test project",
        is_complete=False,
        id=uuid.uuid4(),
        area_id=None,
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
    )
    sessionFixture.add(project_1)

    area_1 = models.Area(name="My first area", id=uuid.uuid4())

    project_2 = models.Project(
        name="My second project",
        description="2nd description",
        is_complete=True,
        id=uuid.uuid4(),
        area_id=area_1.id,
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
    )

    sessionFixture.add(project_1)
    sessionFixture.add(project_2)
    sessionFixture.add(area_1)

    sessionFixture.commit()
    response = clientFixture.get("/projects/")
    # Validate response
    data = response.json()
    assert response.status_code == 200
    assert data[0]["name"] == "My test project"
    assert data[0]["description"] == "Created by My test project"
    assert data[0]["is_complete"] == False
    assert data[0]["area_id"] is None
    assert data[0]["id"] is not None
    assert data[0]["createdAt"] is not None
    assert data[0]["updatedAt"] is not None

    assert data[1]["name"] == "My second project"
    assert data[1]["createdAt"] is not None
    assert data[1]["updatedAt"] is not None
    assert data[1]["id"] is not None
    assert data[1]["description"] == "2nd description"
    assert data[1]["is_complete"] == True
    assert data[1]["area_id"] is not None


def test_get_areas(clientFixture: TestClient, sessionFixture: Session):
    project_1 = models.Project(
        name="My test project",
        description="Created by My test project",
        is_complete=False,
        id=uuid.uuid4(),
        area_id=None,
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
    )
    sessionFixture.add(project_1)

    area_1 = models.Area(name="My first area", id=uuid.uuid4())

    project_2 = models.Project(
        name="My second project",
        description="2nd description",
        is_complete=True,
        id=uuid.uuid4(),
        area_id=area_1.id,
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
    )

    sessionFixture.add(project_1)
    sessionFixture.add(project_2)
    sessionFixture.add(area_1)

    sessionFixture.commit()
    response = clientFixture.get("/projects/")
    # Validate response
    data = response.json()
    assert response.status_code == 200
    assert data[0]["name"] == "My test project"
    assert data[0]["description"] == "Created by My test project"
    assert data[0]["is_complete"] == False
    assert data[0]["area_id"] is None
    assert data[0]["id"] is not None
    assert data[0]["createdAt"] is not None
    assert data[0]["updatedAt"] is not None

    assert data[1]["name"] == "My second project"
    assert data[1]["createdAt"] is not None
    assert data[1]["updatedAt"] is not None
    assert data[1]["id"] is not None
    assert data[1]["description"] == "2nd description"
    assert data[1]["is_complete"] == True
    assert data[1]["area_id"] is not None
