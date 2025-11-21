"""Tests module."""

import datetime
import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from .models.db_models import Project
from .repositories import *
from .models import *
from .main import app
from .schemas.MixinSchemas import TaskContainerTypes
from .schemas.ProjectSchemas import ProjectGet
from .services.project_service import ProjectService


@pytest.fixture
def client():
    yield TestClient(app)


def test_get_list(client):
    project_repo_mock = AsyncMock(spec=ProjectService)

    mockReturnData = [
        ProjectGet(
            name="my project name 1",
            uuid=uuid.uuid4(),
            is_complete=False,
            start_date=datetime.datetime(2025, 10, 1),
            deadline_date=None,
            last_reviewed_date=datetime.datetime.now(),
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            type=TaskContainerTypes.project,
        ),
        ProjectGet(
            name="my project name 2",
            uuid=uuid.uuid4(),
            is_complete=True,
            deadline_date=datetime.datetime(2025, 10, 1),
            start_date=datetime.datetime(2025, 7, 1),
            last_reviewed_date=datetime.datetime.now(),
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            type=TaskContainerTypes.project,
        ),
        ProjectGet(
            name="third project name",
            uuid=uuid.uuid4(),
            is_complete=False,
            description="my description",
            last_reviewed_date=datetime.datetime.now(),
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            type=TaskContainerTypes.project,
        ),
    ]
    project_repo_mock.get_all.return_value = mockReturnData

    app.container.project_repository.override(project_repo_mock)
    response = client.get("/projects")

    response_schemas = []
    for item in response.json():
        project_schema = ProjectGet.model_validate(item)
        response_schemas.append(project_schema)
    assert response.status_code == 200
    assert response_schemas == mockReturnData


# TOdo finish test cases for projects then clone to areas/tasks
# Todo investigate integration vs unit tests
# Todo add something to handle foreign keys

# def test_get_by_id(client):
#     repository_mock = mock.Mock(spec=UserRepository)
#     repository_mock.get_by_id.return_value = User(
#         id=1,
#         email="xyz@email.com",
#         hashed_password="pwd",
#         is_active=True,
#     )
#
#     with app.container.user_repository.override(repository_mock):
#         response = client.get("/users/1")
#
#     assert response.status_code == 200
#     data = response.json()
#     assert data == {
#         "id": 1,
#         "email": "xyz@email.com",
#         "hashed_password": "pwd",
#         "is_active": True,
#     }
#     repository_mock.get_by_id.assert_called_once_with(1)
#
#
# def test_get_by_id_404(client):
#     repository_mock = mock.Mock(spec=UserRepository)
#     repository_mock.get_by_id.side_effect = UserNotFoundError(1)
#
#     with app.container.user_repository.override(repository_mock):
#         response = client.get("/users/1")
#
#     assert response.status_code == 404
#
#
# @mock.patch("webapp.services.uuid4", return_value="xyz")
# def test_add(_, client):
#     repository_mock = mock.Mock(spec=UserRepository)
#     repository_mock.add.return_value = User(
#         id=1,
#         email="xyz@email.com",
#         hashed_password="pwd",
#         is_active=True,
#     )
#
#     with app.container.user_repository.override(repository_mock):
#         response = client.post("/users")
#
#     assert response.status_code == 201
#     data = response.json()
#     assert data == {
#         "id": 1,
#         "email": "xyz@email.com",
#         "hashed_password": "pwd",
#         "is_active": True,
#     }
#     repository_mock.add.assert_called_once_with(email="xyz@email.com", password="pwd")
#
#
# def test_remove(client):
#     repository_mock = mock.Mock(spec=UserRepository)
#
#     with app.container.user_repository.override(repository_mock):
#         response = client.delete("/users/1")
#
#     assert response.status_code == 204
#     repository_mock.delete_by_id.assert_called_once_with(1)
#
#
# def test_remove_404(client):
#     repository_mock = mock.Mock(spec=UserRepository)
#     repository_mock.delete_by_id.side_effect = UserNotFoundError(1)
#
#     with app.container.user_repository.override(repository_mock):
#         response = client.delete("/users/1")
#
#     assert response.status_code == 404
#
#
# def test_status(client):
#     response = client.get("/status")
#     assert response.status_code == 200
#     data = response.json()
#     assert data == {"status": "OK"}
