from freezegun import freeze_time
from unittest.mock import patch

@freeze_time("2025-01-15")  # Date actuelle fixée
def test_cannot_book_past_competition(client):
    """Bug #5: On ne peut pas réserver pour une compétition passée"""
    
    # Mock des données de test contrôlées
    test_competitions = [{
        'name': 'Past Competition',
        'date': '2024-12-01 10:00:00',  # Passée par rapport à 2025-01-15
        'numberOfPlaces': '10'
    }]
    
    test_clubs = [{
        'name': 'Test Club',
        'email': 'test@club.com',
        'points': '5'
    }]
    
    # Patcher les données
    with patch('server.competitions', test_competitions), patch('server.clubs', test_clubs):
            response = client.post('/purchasePlaces',
                                  data={'competition': 'Past Competition',
                                        'club': 'Test Club', 
                                        'places': '1'})
            
            assert b'Cannot book places for past competitions' in response.data

@freeze_time("2025-01-15")
def test_can_book_future_competition(client):
    """On peut réserver pour une compétition future"""
    
    test_competitions = [{
        'name': 'Future Competition',
        'date': '2025-12-01 10:00:00',  # Future par rapport à 2025-01-15
        'numberOfPlaces': '10'
    }]
    
    test_clubs = [{
        'name': 'Test Club',
        'email': 'test@club.com',
        'points': '5'
    }]
    
    with patch('server.competitions', test_competitions), patch('server.clubs', test_clubs):
            response = client.post('/purchasePlaces',
                                  data={'competition': 'Future Competition',
                                        'club': 'Test Club', 
                                        'places': '1'})
            
            assert b'Great-booking complete!' in response.data
            # Vérification de la mise à jour des points
            assert test_clubs[0]['points'] == '4'