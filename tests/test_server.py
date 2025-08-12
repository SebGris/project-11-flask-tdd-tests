import pytest
from server import app as flask_app

# def func(x):
#     return x + 1


# def test_answer():
#     assert func(3) == 4

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture()
def client(app):
    return app.test_client()

def test_request_example(client):
    response = client.get("/")
    assert b"Welcome to the GUDLFT Registration Portal!" in response.data