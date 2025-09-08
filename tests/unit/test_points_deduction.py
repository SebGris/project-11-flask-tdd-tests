from freezegun import freeze_time
from unittest.mock import patch

@freeze_time("2025-01-15")
def test_points_calculation_is_correct(client):
    """Test que les points sont correctement déduits après une réservation"""
    
    # Données de test contrôlées
    test_competitions = [{
        'name': 'Test Competition',
        'date': '2025-06-01 10:00:00',  # Future vs 2025-01-15
        'numberOfPlaces': '50'  # Assez de places disponibles
    }]
    
    test_clubs = [{
        'name': 'Test Club',
        'email': 'test@club.com',
        'points': '15'  # Points initiaux clairement définis
    }]
    
    places_to_book = 3
    expected_points_after = 15 - places_to_book  # 12 points attendus
    
    with patch('server.competitions', test_competitions):
        with patch('server.clubs', test_clubs):
            response = client.post('/purchasePlaces',
                                  data={'competition': 'Test Competition',
                                        'club': 'Test Club',
                                        'places': str(places_to_book)})
            
            # Vérifier que la réservation a réussi
            assert b'Great-booking complete!' in response.data
            
            # Vérifier que les points sont correctement affichés
            assert f'Points available: {expected_points_after}'.encode() in response.data