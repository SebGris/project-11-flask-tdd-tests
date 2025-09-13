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
    expected_points_after = int(test_clubs[0]['points']) - places_to_book
    initial_places = int(test_competitions[0]['numberOfPlaces'])
    
    with patch('server.competitions', test_competitions), patch('server.clubs', test_clubs):
        response = client.post('/purchasePlaces',
                               data={'competition': test_competitions[0]['name'],
                                     'club': test_clubs[0]['name'],
                                     'places': str(places_to_book)})
            
        # Vérifier que la réservation a réussi
        assert b'Great-booking complete!' in response.data
        
        # Vérifier que les points sont correctement affichés
        assert f'Points available: {expected_points_after}'.encode() in response.data
        
        # Vérifier que le dictionnaire est bien modifié
        assert test_clubs[0]['points'] == str(expected_points_after)

        # Vérifier aussi que les places de la compétition sont mises à jour
        assert str(test_competitions[0]['numberOfPlaces']) == str(initial_places - places_to_book)