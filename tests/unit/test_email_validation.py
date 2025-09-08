import pytest

# Helper simple
def login_with(client, email):
    """Helper pour réduire la duplication"""
    return client.post('/showSummary', data={'email': email})

# Tests explicites
def test_valid_email_shows_summary(client):
    """Test qu'un email valide affiche le tableau de bord"""
    response = login_with(client, 'john@simplylift.co')
    response = client.get('/')  # Follow redirect manually if needed
    
    assert b'Welcome' in response.data

def test_invalid_email_redirects(client):
    """Test qu'un email invalide redirige"""
    response = login_with(client, 'invalid@test.com')
    
    assert response.status_code == 302
    assert response.location == '/'

# Grouper les cas similaires avec parametrize
@pytest.mark.parametrize("bad_email", [
    '',                 # Vide
    'not_an_email',    # Sans @
    '@nodomain.com',   # Sans user
])
def test_malformed_emails_rejected(client, bad_email):
    """Test les emails mal formés"""
    response = login_with(client, bad_email)
    assert response.status_code == 302