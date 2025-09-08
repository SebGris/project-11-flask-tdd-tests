def test_points_route_exists(client):
    """La route /points doit exister"""
    response = client.get('/points')
    assert response.status_code == 200

def test_points_display_shows_all_clubs(client):
    """La page /points doit afficher tous les clubs et leurs points"""
    response = client.get('/points')
    
    # Vérifier que tous les clubs sont affichés
    assert b'Simply Lift' in response.data
    assert b'Iron Temple' in response.data
    assert b'She Lifts' in response.data
    
    # Vérifier que les points sont affichés
    assert b'13' in response.data  # Simply Lift
    assert b'4' in response.data   # Iron Temple
    assert b'12' in response.data  # She Lifts