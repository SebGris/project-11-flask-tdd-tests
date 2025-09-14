from freezegun import freeze_time
from unittest.mock import patch  # ou monkeypatch si vous préférez

@freeze_time("2025-01-15")
def test_cannot_book_past_competition(client):
    """Bug #5: On ne peut pas réserver pour une compétition passée"""
    
    test_competitions = [{
        'name': 'Past Competition',
        'date': '2024-12-01 10:00:00',
        'numberOfPlaces': '10'
    }]
    
    test_clubs = [{
        'name': 'Test Club',
        'email': 'test@club.com',
        'points': '5'
    }]
    
    with patch('server.competitions', test_competitions), patch('server.clubs', test_clubs):
        response = client.post('/purchasePlaces',
                              data={'competition': test_competitions[0]['name'],
                                    'club': test_clubs[0]['name'],
                                    'places': '1'})
        
        assert b'Cannot book places for past competitions' in response.data

@freeze_time("2025-01-15")
def test_can_book_future_competition(client):
    """On peut réserver pour une compétition future"""
    
    test_competitions = [{
        'name': 'Future Competition',
        'date': '2025-12-01 10:00:00',
        'numberOfPlaces': '10'
    }]
    
    test_clubs = [{
        'name': 'Test Club',
        'email': 'test@club.com',
        'points': '5'
    }]
    
    with patch('server.competitions', test_competitions), patch('server.clubs', test_clubs):
        response = client.post('/purchasePlaces',
                              data={'competition': test_competitions[0]['name'],
                                    'club': test_clubs[0]['name'],
                                    'places': '1'})
        
        assert b'Great-booking complete!' in response.data
        # Vérification de la mise à jour des points
        assert test_clubs[0]['points'] == '4'