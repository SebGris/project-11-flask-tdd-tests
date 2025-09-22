import pytest
from freezegun import freeze_time


def post_booking(client, monkeypatch, comp, club, places, bookings=None):
    """Helper compact pour les tests de réservation"""
    monkeypatch.setattr('server.competitions', [comp])
    monkeypatch.setattr('server.clubs', [club])
    if bookings:
        monkeypatch.setattr('server.bookings', bookings)
    return client.post('/purchasePlaces', data={
        'competition': comp['name'],
        'club': club['name'],
        'places': str(places)
    })


@freeze_time("2025-01-15")
class TestBookingValidations:
    """Tests groupés par scénarios de validation"""

    def test_past_competition(self, client, monkeypatch,
                              base_club, base_competition):
        """Compétition passée"""
        base_club['points'] = '20'
        base_competition['date'] = '2024-01-01 10:00:00'

        resp = post_booking(
            client, monkeypatch, base_competition, base_club, 1
        )
        assert b'Cannot book places for past competitions.' in resp.data

    def test_zero_and_negative_places(self, client, monkeypatch,
                                      base_club, base_competition):
        """0 ou places négatives"""
        base_club['points'] = '20'

        # Test 0 places
        resp = post_booking(
            client, monkeypatch, base_competition, base_club, 0
        )
        assert b'You must book at least 1 place.' in resp.data

        # Test places négatives
        resp = post_booking(
            client, monkeypatch, base_competition, base_club, -5
        )
        assert b'You must book at least 1 place.' in resp.data

    def test_more_than_available(self, client, monkeypatch,
                                 base_club, base_competition):
        """Plus de places que disponibles"""
        base_club['points'] = '20'
        base_competition['numberOfPlaces'] = '4'

        resp = post_booking(
            client, monkeypatch, base_competition, base_club, 8
        )
        assert b'Not enough places available.' in resp.data

    def test_more_than_twelve(self, client, monkeypatch,
                              base_club, base_competition):
        """Plus de 12 places d'un coup"""
        base_club['points'] = '20'
        base_competition['numberOfPlaces'] = '50'

        resp = post_booking(
            client, monkeypatch, base_competition, base_club, 13
        )
        assert b'Cannot book more than 12 places at once' in resp.data

    def test_cumulative_booking_limit(self, client, monkeypatch,
                                      base_club, base_competition):
        """Un club ne peut pas réserver plus de 12 places au total"""
        base_club['points'] = '20'
        base_competition['numberOfPlaces'] = '20'

        monkeypatch.setattr('server.competitions', [base_competition])
        monkeypatch.setattr('server.clubs', [base_club])
        monkeypatch.setattr('server.bookings', {})

        # Premier: 8 places
        resp = client.post('/purchasePlaces', data={
            'competition': base_competition['name'],
            'club': base_club['name'],
            'places': '8'
        })
        assert b'Great-booking complete!' in resp.data

        # Second: 5 places (total 13, refusé)
        resp = client.post('/purchasePlaces', data={
            'competition': base_competition['name'],
            'club': base_club['name'],
            'places': '5'
        })
        assert b'in total for this competition' in resp.data


@freeze_time("2025-01-15")
@pytest.mark.parametrize("points,places,should_fail", [
    (3, 5, True),   # Plus de places que de points
    (3, 3, False),  # Exactement assez de points
    (3, 2, False),  # Moins de places que de points
    (0, 1, True),   # Aucun point
])
def test_points_validation(client, monkeypatch, base_competition,
                           points, places, should_fail):
    """Test la validation des points"""
    club = {'name': 'Fake Club', 'email': 'fake@club.com',
            'points': str(points)}

    resp = post_booking(client, monkeypatch, base_competition, club, places)

    if should_fail:
        assert b'Not enough points' in resp.data
        assert club['points'] == str(points)
    else:
        assert b'Great-booking complete!' in resp.data
        assert club['points'] == str(points - places)


@pytest.mark.parametrize("comps,clubs,data", [
    # Club invalide
    ([{'name': 'Comp', 'date': '2025-06-01 10:00:00', 'numberOfPlaces': '10'}],
     [],
     {'competition': 'Comp', 'club': 'Invalid', 'places': '2'}),
    # Compétition invalide
    ([],
     [{'name': 'Club', 'email': 'test@club.com', 'points': '10'}],
     {'competition': 'Invalid', 'club': 'Club', 'places': '2'}),
])
def test_invalid_entities(client, monkeypatch, comps, clubs, data):
    """Test avec entités invalides"""
    monkeypatch.setattr('server.competitions', comps)
    monkeypatch.setattr('server.clubs', clubs)
    resp = client.post('/purchasePlaces', data=data)
    assert resp.status_code == 302
    assert resp.location == '/'


@pytest.mark.parametrize("places", ['abc', ''])
def test_invalid_input(client, monkeypatch,
                       base_club, base_competition, places):
    """Test avec valeurs de places invalides"""
    resp = post_booking(client, monkeypatch,
                        base_competition, base_club, places)
    assert b'Nombre de places invalide.' in resp.data
    assert resp.status_code == 200


@freeze_time("2025-01-15")
def test_successful_booking(client, monkeypatch, base_club, base_competition):
    """Test d'une réservation réussie"""
    base_club['points'] = '15'
    base_competition['numberOfPlaces'] = '50'

    resp = post_booking(client, monkeypatch, base_competition, base_club, 3)

    assert b'Great-booking complete!' in resp.data
    assert b'Points available: 12' in resp.data
    assert base_club['points'] == '12'
    assert base_competition['numberOfPlaces'] == '47'
