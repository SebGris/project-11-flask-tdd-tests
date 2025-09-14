import pytest


from server import app

@pytest.fixture
def client():
    """Client de test Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client