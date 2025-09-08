from freezegun import freeze_time
from unittest.mock import patch

@freeze_time("2025-01-15")
def test_cannot_book_more_than_12_places(client):
    """On ne devrait pas pouvoir réserver plus de 12 places"""
    
    # Données de test contrôlées
    test_competitions = [{
        'name': 'Test Competition',
        'date': '2025-06-01 10:00:00',  # Future vs 2025-01-15
        'numberOfPlaces': '50'  # Assez de places
    }]
    
    test_clubs = [{
        'name': 'Test Club',
        'email': 'test@club.com',
        'points': '20'  # Assez de points
    }]
    
    with patch('server.competitions', test_competitions):
        with patch('server.clubs', test_clubs):
            response = client.post('/purchasePlaces',
                                  data={'competition': 'Test Competition',
                                        'club': 'Test Club',
                                        'places': '13'})  # > 12 places
            
            assert b'Cannot book more than 12 places' in response.data