# Version 1 : Simple mais fragile
def test_points_deducted_after_booking(client):
    """Premier test - accepte qu'il soit fragile"""
    response = client.post('/purchasePlaces',
                          data={'competition': 'Spring Festival',
                                'club': 'Simply Lift', 
                                'places': '3'})
    
    assert b'Points available: 10' in response.data  # Hardcodé