def test_cannot_book_more_than_12_places(client):
    """Bug #3: On ne devrait pas pouvoir réserver plus de 12 places"""
    response = client.post('/purchasePlaces',
                          data={'competition': 'Spring Festival',
                                'club': 'Simply Lift', 
                                'places': '13'})
    
    # Le bug : la réservation passe alors qu'elle devrait être refusée
    assert b'Cannot book more than 12 places' in response.data


def test_cannot_book_more_than_12_places_total(client, monkeypatch):
    """
    Un club ne peut pas réserver plus de 12 places au total pour une
    compétition
    """
    competitions = [{
        'name': 'Test Competition',
        'date': '2025-06-01 10:00:00',
        'numberOfPlaces': '20'
    }]
    clubs = [{
        'name': 'Test Club',
        'email': 'test@club.com',
        'points': '20'
    }]

    monkeypatch.setattr('server.competitions', competitions)
    monkeypatch.setattr('server.clubs', clubs)
    monkeypatch.setattr('server.bookings', {})  # ← AJOUTER CETTE LIGNE !

    # Premier achat de 8 places
    response1 = client.post('/purchasePlaces', data={
        'competition': competitions[0]['name'],
        'club': clubs[0]['name'],
        'places': '8'
    })
    assert b'Great-booking complete!' in response1.data

    # Deuxième achat de 5 places (total 13, donc refusé)
    response2 = client.post('/purchasePlaces', data={
        'competition': competitions[0]['name'],
        'club': clubs[0]['name'],
        'places': '5'
    })
    assert (
        b'Cannot book more than 12 places in total for this competition'
        in response2.data
    )
