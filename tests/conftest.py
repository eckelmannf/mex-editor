from collections.abc import Generator
from fastapi.testclient import TestClient
import pytest

from mex.editor.main import create_fastapi


pytest_plugins = ("mex.common.testing.plugin",)


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Return a fastAPI test client initialized with our app."""
    app = create_fastapi()
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
