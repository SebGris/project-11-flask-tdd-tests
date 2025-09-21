import pytest
from datetime import datetime, timedelta


@pytest.fixture
def base_club():
    """Club de base réutilisable"""
    return {'name': 'Fake Club', 'email': 'fake@club.com', 'points': '10'}


@pytest.fixture
def base_competition():
    """Compétition de base réutilisable"""
    future = datetime.now() + timedelta(days=30)
    return {
        'name': 'Test Competition',
        'date': future.strftime("%Y-%m-%d %H:%M:%S"),
        'numberOfPlaces': '15'
    }


@pytest.fixture
def mock_clubs(base_club):
    """Liste minimale de clubs pour le client"""
    return [
        base_club,
        {
            'name': 'Other Club',
            'email': 'other@club.com',
            'points': '20'
        }
    ]


@pytest.fixture
def mock_competitions(base_competition):
    """Liste minimale de compétitions pour le client"""
    return [
        {
            'name': 'Past Comp',
            'date': '2020-03-27 10:00:00',
            'numberOfPlaces': '25'
        },
        base_competition
    ]


@pytest.fixture
def client(monkeypatch, mock_competitions, mock_clubs):
    """Créer un client de test pour l'application Flask"""

    # Import local dans la fixture
    import server

    # Maintenant on peut patcher les variables
    monkeypatch.setattr('server.clubs', mock_clubs)
    monkeypatch.setattr('server.competitions', mock_competitions)
    monkeypatch.setattr('server.bookings', {})

    # Mocker les fonctions de sauvegarde
    monkeypatch.setattr('server.save_clubs', lambda x: None)
    monkeypatch.setattr('server.save_competitions', lambda x: None)
    monkeypatch.setattr('server.save_bookings', lambda x: None)

    server.app.config['TESTING'] = True

    with server.app.test_client() as client:
        yield client
