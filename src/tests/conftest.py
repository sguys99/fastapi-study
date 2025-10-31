import pytest
from fastapi.testclient import TestClient
from main import app

# fixture는 함수형태로 만들어야함
@pytest.fixture
def client():
    return TestClient(app=app)
