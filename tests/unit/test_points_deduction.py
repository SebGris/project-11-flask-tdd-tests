# Version 2 : Améliorée après que ça marche
def test_points_calculation_is_correct(client):
    """Test refactorisé - plus robuste"""
    initial_points = 13  # Documenté explicitement
    places_booked = 3
    expected_points = initial_points - places_booked
    
    response = client.post('/purchasePlaces',
                          data={'competition': 'Spring Festival',
                                'club': 'Simply Lift', 
                                'places': str(places_booked)})
    
    assert f'Points available: {expected_points}'.encode() in response.data