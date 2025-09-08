def test_cannot_book_more_than_12_places(client):
    """Bug #3: On ne devrait pas pouvoir réserver plus de 12 places"""
    response = client.post('/purchasePlaces',
                          data={'competition': 'Spring Festival',
                                'club': 'Simply Lift', 
                                'places': '13'})
    
    # Le bug : la réservation passe alors qu'elle devrait être refusée
    assert b'Cannot book more than 12 places' in response.data