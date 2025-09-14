import pytest
from freezegun import freeze_time


# test_available_places
@freeze_time("2025-01-15")
def test_cannot_book_more_than_available_places(client, monkeypatch):
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

    monkeypatch.setattr('server.competitions', test_competitions)
    monkeypatch.setattr('server.clubs', test_clubs)

    response = client.post(
        '/purchasePlaces',
        data={
            'competition': test_competitions[0]['name'],
            'club': test_clubs[0]['name'],
            'places': '8'
        }
    )  # > 5 places disponibles

    assert b'Not enough places available' in response.data


# test_booking_limit
@freeze_time("2025-01-15")
def test_cannot_book_more_than_12_places(client, monkeypatch):
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

    monkeypatch.setattr('server.competitions', test_competitions)
    monkeypatch.setattr('server.clubs', test_clubs)

    response = client.post(
        '/purchasePlaces',
        data={
            'competition': test_competitions[0]['name'],
            'club': test_clubs[0]['name'],
            'places': '13'
        }
    )  # > 12 places

    assert b'Cannot book more than 12 places' in response.data


# test_past_competition
@freeze_time("2025-01-15")
def test_cannot_book_past_competition(client, monkeypatch):
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

    monkeypatch.setattr('server.competitions', test_competitions)
    monkeypatch.setattr('server.clubs', test_clubs)

    response = client.post(
        '/purchasePlaces',
        data={
            'competition': test_competitions[0]['name'],
            'club': test_clubs[0]['name'],
            'places': '1'
        }
    )

    assert b'Cannot book places for past competitions' in response.data


@freeze_time("2025-01-15")
def test_can_book_future_competition(client, monkeypatch):
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

    monkeypatch.setattr('server.competitions', test_competitions)
    monkeypatch.setattr('server.clubs', test_clubs)

    response = client.post(
        '/purchasePlaces',
        data={
            'competition': test_competitions[0]['name'],
            'club': test_clubs[0]['name'],
            'places': '1'
        }
    )

    assert b'Great-booking complete!' in response.data
    # Vérification de la mise à jour des points
    assert test_clubs[0]['points'] == '4'


# test_points_deduction
@freeze_time("2025-01-15")
def test_points_calculation_is_correct(client, monkeypatch):
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

    monkeypatch.setattr('server.competitions', test_competitions)
    monkeypatch.setattr('server.clubs', test_clubs)

    response = client.post(
        '/purchasePlaces',
        data={
            'competition': test_competitions[0]['name'],
            'club': test_clubs[0]['name'],
            'places': str(places_to_book)
        }
    )

    # Vérifier que la réservation a réussi
    assert b'Great-booking complete!' in response.data

    # Vérifier que les points sont correctement affichés
    assert (
        f'Points available: {expected_points_after}'.encode()
        in response.data
    )

    # Vérifier que le dictionnaire est bien modifié
    assert test_clubs[0]['points'] == str(expected_points_after)

    # Vérifier aussi que les places de la compétition sont mises à jour
    assert str(test_competitions[0]['numberOfPlaces']) == (
        str(initial_places - places_to_book)
    )


# test_points_validation
@pytest.mark.parametrize("points,places_to_book,should_fail", [
    (3, 5, True),   # Plus de places que de points
    (3, 3, False),  # Exactement assez de points
    (3, 2, False),  # Moins de places que de points
    (0, 1, True),   # Aucun point
])
@freeze_time("2025-01-15")
def test_points_validation_for_booking(
    client, monkeypatch, points, places_to_book, should_fail
):
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

    response = client.post(
        '/purchasePlaces',
        data={
            'competition': test_competitions[0]['name'],
            'club': test_clubs[0]['name'],
            'places': str(places_to_book)
        }
    )

    if should_fail:
        # Cas d'échec : vérifier erreur et état inchangé
        assert b'Not enough points' in response.data
        assert test_clubs[0]['points'] == str(points)  # Points inchangés
        assert test_competitions[0]['numberOfPlaces'] == '50'  # pl inchangées
    else:
        # Cas de succès : vérifier mise à jour
        assert b'Great-booking complete!' in response.data
        assert test_clubs[0]['points'] == str(points - places_to_book)
