import pytest


from server import app


@pytest.fixture
def client():
    """Client de test Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def fake_clubs():
    return [
        {'name': 'Fake Club', 'email': 'fake@club.com', 'points': '10'},
        {'name': 'Other Club', 'email': 'other@club.com', 'points': '20'}
    ]