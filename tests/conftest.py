import pytest
import server


from server import app


@pytest.fixture
def client():
    """Client de test Flask basique - chaque test gère ses propres données"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def fake_clubs():
    return [
        {'name': 'Fake Club', 'email': 'fake@club.com', 'points': '10'},
        {'name': 'Other Club', 'email': 'other@club.com', 'points': '20'}
    ]


@pytest.fixture
def fake_competitions():
    return [
        {
            'name': 'Fake Competition',
            'date': '2025-12-31 10:00:00',
            'numberOfPlaces': '5'
        },
        {
            'name': 'Other Competition',
            'date': '2025-11-30 10:00:00',
            'numberOfPlaces': '10'
        }
    ]


@pytest.fixture
def mock_app_data(monkeypatch, fake_clubs, fake_competitions):
    """Fixture qui applique automatiquement les mocks"""
    monkeypatch.setattr(server, 'clubs', fake_clubs)
    monkeypatch.setattr(server, 'competitions', fake_competitions)
