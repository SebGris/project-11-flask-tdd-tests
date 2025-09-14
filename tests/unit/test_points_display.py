def test_points_route_exists(client):
    """La route /points doit exister"""
    response = client.get('/points')
    assert response.status_code == 200


def test_points_display_shows_all_clubs(client, monkeypatch, fake_clubs):
    """La page /points doit afficher tous les clubs et leurs points"""
    # Utiliser la fixture fake_clubs
    monkeypatch.setattr('server.clubs', fake_clubs)

    response = client.get('/points')

    # Vérifier que les clubs de la fixture sont affichés
    assert b'Fake Club' in response.data
    assert b'Other Club' in response.data

    # Vérifier que les points sont affichés
    assert b'10' in response.data  # Fake Club
    assert b'20' in response.data  # Other Club
