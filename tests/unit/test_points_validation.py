from freezegun import freeze_time
from unittest.mock import patch

@freeze_time("2025-01-15")
def test_cannot_book_more_places_than_points(client):
    """On ne peut pas réserver plus de places qu'on a de points"""
    
    test_competitions = [{
        'name': 'Test Competition',
        'date': '2025-06-01 10:00:00',
        'numberOfPlaces': '50'
    }]
    
    test_clubs = [{
        'name': 'Test Club',
        'email': 'test@club.com',
        'points': '3'  # Seulement 3 points
    }]
    
    with patch('server.competitions', test_competitions):
        with patch('server.clubs', test_clubs):
            response = client.post('/purchasePlaces',
                                  data={'competition': 'Test Competition',
                                        'club': 'Test Club',
                                        'places': '5'})  # > 3 points disponibles
            
            assert b'Not enough points' in response.data