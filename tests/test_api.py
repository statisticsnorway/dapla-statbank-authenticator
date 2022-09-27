import toml
import os
from fastapi.testclient import TestClient

from pathlib import Path
from app import __version__
from app.main import app, get_project_and_name, get_secret_manager_client
from unittest.mock import Mock


def test_versions_are_in_sync():
    """Checks if the pyproject.toml and package.__init__.py __version__ are in sync."""

    path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    pyproject = toml.loads(open(str(path)).read())
    pyproject_version = pyproject["tool"]["poetry"]["version"]

    package_init_version = __version__

    assert package_init_version == pyproject_version


def test_encrypt():
    os.environ['CIPHER_KEY'] = '@NcRfUjXn2r5u8x/'
    with TestClient(app) as client:
        response = client.post("/encrypt", json={
            "message": "mysecretmessage"
        })
        assert response.status_code == 200
        # The same cipher will always create the same result
        assert response.json() == {
            "message": 'dQB+Eaf751En6/j4TQtrcg=='
        }


def test_encrypt_with_sm_key():
    os.environ['CIPHER_KEY'] = 'sm://my-project/my-key'
    sm_client_mock = Mock()
    sm_response = {
        "payload": "dQB+Eaf751En6/j4TQtrcg=="
    }
    sm_client_mock.access_secret_version = lambda arg: sm_response
    with TestClient(app) as client:
        app.dependency_overrides[get_secret_manager_client] = lambda: sm_client_mock
        response = client.post("/encrypt", json={
            "message": "mysecretmessage"
        })
        assert response.status_code == 200
        # The same cipher will always create the same result
        assert response.json() == {
            "message": 'dQB+Eaf751En6/j4TQtrcg=='
        }


def test_parsing():
    project_id, name, version = get_project_and_name('sm://my-project/my-secret')
    assert project_id == 'my-project'
    assert name == 'my-secret'
    assert version == 'latest'

    project_id, name, version = get_project_and_name('sm://my-project/my-secret#1')
    assert project_id == 'my-project'
    assert name == 'my-secret'
    assert version == '1'
