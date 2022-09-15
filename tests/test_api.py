import toml
import os
from fastapi.testclient import TestClient

from pathlib import Path
from app import __version__
from app.main import app

client = TestClient(app)


def test_versions_are_in_sync():
    """Checks if the pyproject.toml and package.__init__.py __version__ are in sync."""

    path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    pyproject = toml.loads(open(str(path)).read())
    pyproject_version = pyproject["tool"]["poetry"]["version"]

    package_init_version = __version__

    assert package_init_version == pyproject_version


def test_encrypt():
    os.environ['CIPHER_KEY'] = '@NcRfUjXn2r5u8x/'
    response = client.post("/encrypt", json={
        "message": "mysecretmessage"
    })
    assert response.status_code == 200
    # The same cipher will always create the same result
    assert response.json() == {
        "message": 'dQB+Eaf751En6/j4TQtrcg=='
    }
