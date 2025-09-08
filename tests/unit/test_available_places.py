def test_cannot_book_more_than_available_places(client):
    """Bug #6: Ne pas réserver plus de places que disponibles"""
    # Fall Classic a 13 places
    response = client.post('/purchasePlaces',
                          data={'competition': 'Fall Classic',
                                'club': 'Simply Lift', 
                                'places': '15'})  # Plus que les 13 disponibles
    
    assert b'Not enough places available' in response.data