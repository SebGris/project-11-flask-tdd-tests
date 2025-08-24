import pytest
from server import clubs


@pytest.mark.unit
@pytest.mark.issue1
class TestEmailValidationUnit:
    """Tests unitaires pour la validation d'email"""
    
    def test_find_club_by_valid_email(self, mock_clubs):
        """Test unitaire : recherche d'un club avec un email valide"""
        # Act : Rechercher un club existant
        email_to_find = 'test1@example.com'
        found_club = next(
            (club for club in mock_clubs if club['email'] == email_to_find), 
            None
        )
        
        # Assert : Vérifier que le club est trouvé
        assert found_club is not None
        assert found_club['name'] == 'Test Club 1'
        assert found_club['email'] == 'test1@example.com'
        assert found_club['points'] == '15'
    
    def test_find_club_by_invalid_email(self, mock_clubs):
        """Test unitaire : recherche d'un club avec un email invalide"""
        # Act
        email_to_find = 'inexistant@example.com'
        found_club = next(
            (club for club in mock_clubs if club['email'] == email_to_find), 
            None
        )
        
        # Assert
        assert found_club is None
    

@pytest.mark.functional
@pytest.mark.issue1
class TestEmailValidationFunctional:
    """Tests fonctionnels pour la validation d'email"""
    
    def test_valid_email_shows_welcome_page(self, client):
        """Test fonctionnel : un email valide affiche la page welcome"""
        # Skip si pas de clubs dans le fichier JSON
        if not clubs:
            pytest.skip("Aucun club disponible dans clubs.json")
        
        # Arrange : Utiliser le premier club disponible
        valid_email = clubs[0]['email']
        
        # Act : Poster l'email
        response = client.post('/showSummary', 
                              data={'email': valid_email},
                              follow_redirects=True)
        
        # Assert : Vérifications multiples
        assert response.status_code == 200
        assert b'Welcome' in response.data
        assert valid_email.encode() in response.data
        assert b'Points available:' in response.data
        assert b'Competitions:' in response.data
    
    def test_invalid_email_shows_error_message(self, client):
        """Test fonctionnel : un email invalide affiche un message d'erreur"""
        # Arrange
        invalid_email = 'nexistepas@test.com'
        
        # Act
        response = client.post('/showSummary',
                              data={'email': invalid_email},
                              follow_redirects=True)
        
        # Assert
        assert response.status_code == 200
        # Le message d'erreur attendu (ce test échouera avant le fix)
        assert 'Désolé, cette adresse e-mail est introuvable.'.encode() in response.data, f"Message d'erreur introuvable pour {invalid_email}"
        # Doit rester sur la page d'accueil
        assert b'Welcome to the GUDLFT Registration Portal' in response.data
        # Ne doit pas afficher la page welcome
        assert b'Points available:' not in response.data
    
    def test_empty_email_field(self, client):
        """Test fonctionnel : champ email vide"""
        response = client.post('/showSummary',
                            data={'email': ''},
                            follow_redirects=True)
        
        assert response.status_code == 200
        # Nouveau message pour email vide
        assert b'Veuillez saisir une adresse e-mail' in response.data
    
    def test_missing_email_parameter(self, client):
        """Test fonctionnel : paramètre email manquant dans la requête"""
        # Act
        response = client.post('/showSummary',
                              data={},
                              follow_redirects=True)
        
        # Assert : L'application ne doit pas planter (500)
        assert response.status_code in [200, 400, 302], f"L'app a planté avec code {response.status_code}"

    def test_email_with_special_characters(self, client):
        """Test fonctionnel : email avec caractères spéciaux"""
        special_emails = [
            "test+tag@example.com",
            "test.name@example.com",
            "test@sub.domain.com"
        ]
        
        for email in special_emails:
            response = client.post('/showSummary',
                                  data={'email': email},
                                  follow_redirects=True)
            
            # L'application ne doit pas planter
            assert response.status_code == 200
            # Doit afficher un message (erreur ou succès)
            assert len(response.data) > 0
    
    def test_sql_injection_attempt(self, client):
        """Test de sécurité : tentative d'injection SQL"""
        malicious_email = "'; DROP TABLE clubs; --"
        
        response = client.post('/showSummary',
                              data={'email': malicious_email},
                              follow_redirects=True)
        
        # L'application doit survivre et traiter comme email invalide
        assert response.status_code == 200
        assert b'introuvable' in response.data or b'error' in response.data.lower()
    
    def test_very_long_email(self, client):
        """Test fonctionnel : email extrêmement long"""
        long_email = "a" * 500 + "@example.com"
        
        response = client.post('/showSummary',
                              data={'email': long_email},
                              follow_redirects=True)
        
        # Ne doit pas planter
        assert response.status_code == 200
    
    def test_multiple_rapid_requests(self, client):
        """Test fonctionnel : requêtes rapides multiples"""
        # Simuler plusieurs tentatives rapides (détection de problèmes de concurrence)
        for i in range(5):
            response = client.post('/showSummary',
                                  data={'email': f'test{i}@example.com'},
                                  follow_redirects=True)
            assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.issue1
class TestEmailValidationIntegration:
    """Tests d'intégration pour vérifier le workflow complet"""
    
    def test_complete_login_workflow(self, client):
        """Test d'intégration : workflow complet de connexion"""
        # 1. Accéder à la page d'accueil
        response = client.get('/')
        assert response.status_code == 200
        assert b'GUDLFT Registration' in response.data
        
        # 2. Tenter une connexion avec email invalide
        response = client.post('/showSummary',
                              data={'email': 'invalid@test.com'},
                              follow_redirects=True)
        assert response.status_code == 200
        assert b'introuvable' in response.data
        
        # 3. Se connecter avec un email valide (si disponible)
        if clubs:
            response = client.post('/showSummary',
                                  data={'email': clubs[0]['email']},
                                  follow_redirects=True)
            assert response.status_code == 200
            assert b'Welcome' in response.data
            
            # 4. Vérifier la déconnexion
            response = client.get('/logout', follow_redirects=True)
            assert response.status_code == 200
            assert b'GUDLFT Registration Portal' in response.data