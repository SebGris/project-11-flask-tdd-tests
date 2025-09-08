from freezegun import freeze_time
from unittest.mock import patch

@freeze_time("2025-01-15")
def test_cannot_book_more_than_available_places(client):
    """Ne pas réserver plus de places que disponibles"""
    
    test_competitions = [{
        'name': 'Small Competition',
        'date': '2025-06-01 10:00:00',
        'numberOfPlaces': '5'  # Seulement 5 places
    }]
    
    test_clubs = [{
        'name': 'Test Club',
        'email': 'test@club.com',
        'points': '20'  # Assez de points
    }]
    
    with patch('server.competitions', test_competitions):
        with patch('server.clubs', test_clubs):
            response = client.post('/purchasePlaces',
                                  data={'competition': 'Small Competition',
                                        'club': 'Test Club',
                                        'places': '8'})  # > 5 places disponibles
            
            assert b'Not enough places available' in response.data