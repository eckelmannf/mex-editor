from collections.abc import Generator
import pytest
import requests
from fastapi.testclient import TestClient

from mex.editor.main import create_fastapi


def test_main_api_hello(client: TestClient) -> None:
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == "Hello from mex-editor API"


def test_main_app(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "</html>" in response.text
    assert "<app-root></app-root>" in response.text
