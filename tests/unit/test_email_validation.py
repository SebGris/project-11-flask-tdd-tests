import pytest


def test_homepage(client):
    """Test de la page d'accueil"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'GUDLFT Registration' in response.data


def test_valid_email_shows_summary(client):
    """Test qu'un email valide affiche le tableau de bord"""
    response = client.post('/showSummary', data={'email': 'fake@club.com'})

    assert response.status_code == 200
    assert b'Welcome, fake@club.com' in response.data
    assert b'Points available: 10' in response.data    # Points du fake club
    assert b'Test Competition' in response.data        # Compétition mockée


@pytest.mark.parametrize("email,should_succeed", [
    ('other@club.com', True),
    ('invalid@test.com', False),
    ('', False),
    ('not_an_email', False),
])
def test_email_validation_matrix(client, email, should_succeed):
    """Matrice de tests pour validation d'email"""
    response = client.post('/showSummary', data={'email': email})

    if should_succeed:
        assert response.status_code == 200
        assert b'Welcome' in response.data
    else:
        assert response.status_code == 302
        assert response.location == '/'


def test_logout_redirects_to_index(client):
    """Test que logout redirige vers la page d'accueil"""
    response = client.get('/logout')

    assert response.status_code == 302
    assert response.location == '/'
