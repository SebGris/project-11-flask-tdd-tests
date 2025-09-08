def test_points_display_shows_all_clubs(client):
    """La page /points doit afficher tous les clubs et leurs points"""
    response = client.get('/points')
    
    # DEBUG: Voir le contenu exact
    content = response.data.decode()
    print(f"\n=== DEBUG CONTENT ===")
    print(repr(content))
    print(f"'13' present: {'13' in content}")
    print(f"b'13' in response.data: {b'13' in response.data}")
    
    # Tests normaux
    assert b'Simply Lift' in response.data
    assert b'Iron Temple' in response.data
    assert b'She Lifts' in response.data

    # Le test qui échoue
    assert b'13' in response.data  # Simply Lift