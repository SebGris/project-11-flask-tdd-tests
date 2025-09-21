import pytest
from unittest.mock import patch
from server import app, clubs, competitions


@pytest.fixture
def client():
    """Client avec sauvegarde mockée"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with patch('server.save_clubs'), \
             patch('server.save_competitions'), \
             patch('server.save_bookings'):
            yield client


def test_parcours_complet_secretaire(client):
    """Test du parcours complet décrit dans les specs"""
    # Utiliser un vrai email depuis clubs.json
    test_club = clubs[0]  # Premier club dans la liste
    test_email = test_club['email']
    initial_points = test_club['points']

    # 1. Connexion
    response = client.post('/showSummary',
                           data={'email': test_email})
    assert response.status_code == 200
    assert f"Welcome, {test_email}".encode() in response.data
    assert f"Points available: {initial_points}".encode() in response.data

    # 2. Accéder à une compétition future
    # Chercher une compétition avec des places
    valid_comp = next((c for c in competitions
                       if int(c['numberOfPlaces']) > 0), None)
    if valid_comp:
        response = client.get(
            f'/book/{valid_comp["name"]}/{test_club["name"]}'
        )
        assert response.status_code == 200
        assert b'Places available' in response.data


def test_erreur_pas_assez_de_points(client):
    """Test du message d'erreur si pas assez de points"""
    # Iron Temple a 4 points
    poor_club = min(clubs, key=lambda c: int(c['points']))

    response = client.post('/showSummary',
                           data={'email': poor_club['email']})
    assert response.status_code == 200

    # Essayer de réserver 5 places (plus que ses 4 points)
    response = client.post('/purchasePlaces', data={
        'competition': 'Test Future Competition',  # Toujours future
        'club': poor_club['name'],
        'places': '5'
    })

    # Vérifier le message d'erreur ou au moins que ça n'a pas marché
    assert (b'Not enough points' in response.data or
            b'Great-booking complete!' not in response.data)


def test_limite_12_places_maximum(client):
    """Test qu'on ne peut pas réserver plus de 12 places"""
    rich_club = max(clubs, key=lambda c: int(c['points']))

    response = client.post('/showSummary',
                           data={'email': rich_club['email']})
    assert response.status_code == 200

    # Essayer de réserver 13 places
    response = client.post('/purchasePlaces', data={
        'competition': 'Test Future Competition',
        'club': rich_club['name'],
        'places': '13'
    })

    # La réservation doit échouer (peu importe la raison)
    assert b'Great-booking complete!' not in response.data
    # Et les points ne doivent pas changer
    assert rich_club['points'] == '12'  # Toujours 12


def test_tableau_public_points_sans_connexion(client):
    """Test du tableau public des points (Phase 2)"""
    response = client.get('/points')
    assert response.status_code == 200

    # Vérifier que tous les clubs sont affichés
    for club in clubs:
        assert club['name'].encode() in response.data
        assert club['points'].encode() in response.data


def test_deconnexion_secretaire(client):
    """Test de la déconnexion"""
    # Se connecter avec n'importe quel club
    test_email = clubs[0]['email']

    response = client.post('/showSummary',
                           data={'email': test_email})
    assert response.status_code == 200

    # Se déconnecter
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.location == '/'


def test_email_invalide_connexion(client):
    """Test avec un email non enregistré"""
    response = client.post('/showSummary',
                           data={'email': 'invalid@test.com'},
                           follow_redirects=True)
    assert response.status_code == 200
    # Le message peut être encodé en HTML
    assert (b"Sorry, that email wasn&#39;t found" in response.data or
            b"Sorry, that email wasn't found" in response.data)


def test_reservation_reussie(client):
    """Test d'une réservation réussie simple"""
    # Prendre le premier club et première compétition valide
    test_club = clubs[0]
    test_email = test_club['email']

    # Se connecter
    response = client.post('/showSummary',
                           data={'email': test_email})
    assert response.status_code == 200

    # Trouver une compétition future avec des places
    from datetime import datetime
    for comp in competitions:
        comp_date = datetime.strptime(comp['date'], "%Y-%m-%d %H:%M:%S")
        if comp_date > datetime.now() and int(comp['numberOfPlaces']) > 0:
            # Réserver 1 place
            response = client.post('/purchasePlaces', data={
                'competition': comp['name'],
                'club': test_club['name'],
                'places': '1'
            })
            assert b'Great-booking complete!' in response.data
            break
