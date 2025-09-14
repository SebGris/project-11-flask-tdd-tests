import pytest

def login_with(client, email):
    """Helper pour réduire la duplication"""
    return client.post('/showSummary', data={'email': email})

def test_valid_email_shows_summary(client, mock_app_data):
    """Test qu'un email valide affiche le tableau de bord"""
    response = login_with(client, 'fake@club.com')
    
    assert response.status_code == 200
    assert b'Welcome, fake@club.com' in response.data  # Le template affiche l'email
    assert b'Points available: 10' in response.data    # Points du fake club
    assert b'Fake Competition' in response.data        # Compétition mockée

def test_invalid_email_redirects(client, mock_app_data):
    """Test qu'un email invalide redirige"""
    response = login_with(client, 'nonexistent@email.com')
    
    assert response.status_code == 302
    assert response.location == '/'

@pytest.mark.parametrize("email,should_succeed", [
    ('fake@club.com', True),
    ('other@club.com', True),
    ('invalid@test.com', False),
    ('', False),
    ('not_an_email', False),
])
def test_email_validation_matrix(client, mock_app_data, email, should_succeed):
    """Matrice de tests pour validation d'email"""
    response = login_with(client, email)
    
    if should_succeed:
        assert response.status_code == 200
        assert b'Welcome' in response.data
    else:
        assert response.status_code == 302
        assert response.location == '/'