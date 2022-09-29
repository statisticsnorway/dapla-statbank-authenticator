import toml
import os
from fastapi.testclient import TestClient

from pathlib import Path
from app import __version__
from app.main import app, get_project_and_name, get_sm_client
from google.cloud.secretmanager import SecretManagerServiceClient, AccessSecretVersionResponse, SecretPayload
from google.auth import credentials

CIPHER_KEY_16_DIGIT = '@NcRfUjXn2r5u8x/'

client = TestClient(app)
# Local instance of Secret Manager Service that can be used to fake reponses
sm_client = SecretManagerServiceClient(credentials=credentials.AnonymousCredentials)
app.dependency_overrides[get_sm_client] = lambda: sm_client


def test_versions_are_in_sync():
    """Checks if the pyproject.toml and package.__init__.py __version__ are in sync."""

    path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    pyproject = toml.loads(open(str(path)).read())
    pyproject_version = pyproject["tool"]["poetry"]["version"]

    package_init_version = __version__

    assert package_init_version == pyproject_version


def test_encrypt_without_env_variable():
    response = client.post("/encrypt", json={
        "message": "mysecretmessage"
    })
    assert response.status_code == 500
    assert response.json() == {'detail': 'Missing environment variable: CIPHER_KEY'}


def test_encrypt_with_invalid_cipher():
    os.environ['CIPHER_KEY'] = 'invalid_cipher'
    response = client.post("/encrypt", json={
        "message": "mysecretmessage"
    })
    assert response.status_code == 500
    assert response.json() == {'detail': 'CIPHER_KEY must be of length 16'}


def test_encrypt():
    os.environ['CIPHER_KEY'] = CIPHER_KEY_16_DIGIT
    response = client.post("/encrypt", json={
        "message": "mysecretmessage"
    })
    assert response.status_code == 200
    # The same cipher will always create the same result
    assert response.json() == {
        "message": 'dQB+Eaf751En6/j4TQtrcg=='
    }


def test_encrypt_with_sm_key():
    # Fake the response from Secret Manager
    sm_client.access_secret_version = lambda request: AccessSecretVersionResponse(
        payload=SecretPayload(data=CIPHER_KEY_16_DIGIT.encode("UTF-8"))
    )
    os.environ['CIPHER_KEY'] = 'sm://my-project/my-key'
    response = client.post("/encrypt", json={
        "message": "mysecretmessage"
    })
    assert response.status_code == 200
    # The same cipher will always create the same result
    assert response.json() == {
        "message": 'dQB+Eaf751En6/j4TQtrcg=='
    }


def test_parse_with_default_version():
    project_id, name, version = get_project_and_name('sm://my-project/my-secret')
    assert project_id == 'my-project'
    assert name == 'my-secret'
    assert version == 'latest'


def test_parse_with_version():
    project_id, name, version = get_project_and_name('sm://my-project/my-secret#1')
    assert project_id == 'my-project'
    assert name == 'my-secret'
    assert version == '1'
