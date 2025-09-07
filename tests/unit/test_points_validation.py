def test_cannot_book_more_places_than_points(client):
    """Bug #4: On ne peut pas réserver plus de places qu'on a de points"""
    # Iron Temple n'a que 4 points
    response = client.post('/purchasePlaces',
                          data={'competition': 'Spring Festival',
                                'club': 'Iron Temple', 
                                'places': '5'})
    
    # Devrait être refusé
    assert b'Not enough points' in response.data