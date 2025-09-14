import pytest
from freezegun import freeze_time

@pytest.mark.parametrize("points,places_to_book,should_fail", [
    (3, 5, True),   # Plus de places que de points
    (3, 3, False),  # Exactement assez de points
    (3, 2, False),  # Moins de places que de points
    (0, 1, True),   # Aucun point
])
@freeze_time("2025-01-15")
def test_points_validation_for_booking(client, monkeypatch, points, places_to_book, should_fail):
    """Test la validation des points pour différents cas"""
    
    test_competitions = [{
        'name': 'Test Competition',
        'date': '2025-06-01 10:00:00',
        'numberOfPlaces': '50'
    }]
   
    test_clubs = [{
        'name': 'Test Club',
        'email': 'test@club.com',
        'points': str(points)
    }]
    
    # Utiliser monkeypatch au lieu de patch
    monkeypatch.setattr('server.competitions', test_competitions)
    monkeypatch.setattr('server.clubs', test_clubs)
    
    response = client.post('/purchasePlaces',
                          data={'competition': test_competitions[0]['name'],
                                'club': test_clubs[0]['name'],
                                'places': str(places_to_book)})
    
    if should_fail:
        # Cas d'échec : vérifier erreur et état inchangé
        assert b'Not enough points' in response.data
        assert test_clubs[0]['points'] == str(points)  # Points inchangés
        assert test_competitions[0]['numberOfPlaces'] == '50'  # Places inchangées
    else:
        # Cas de succès : vérifier mise à jour
        assert b'Great-booking complete!' in response.data
        assert test_clubs[0]['points'] == str(points - places_to_book)