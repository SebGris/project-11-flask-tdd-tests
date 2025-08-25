import pytest
from datetime import datetime, timedelta
from server import clubs, competitions


@pytest.mark.functional
@pytest.mark.issue5
class TestPastCompetitionsBooking:
    """Tests fonctionnels pour empêcher les réservations sur compétitions passées"""
    
    @pytest.fixture
    def past_competition(self):
        """Fixture pour une compétition passée"""
        return {
            'name': 'Past Competition Test',
            'date': '2020-01-01 10:00:00',  # Date dans le passé
            'numberOfPlaces': '10'
        }
    
    @pytest.fixture
    def future_competition(self):
        """Fixture pour une compétition future"""
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        return {
            'name': 'Future Competition Test',
            'date': future_date,
            'numberOfPlaces': '10'
        }
    
    def test_past_competition_booking_page_access(self, client):
        """Test : l'accès à la page de réservation pour une compétition passée devrait être bloqué"""
        if not clubs or not competitions:
            pytest.skip("Pas de données disponibles")
        
        # Trouver une compétition passée dans les données réelles
        past_comp = None
        for comp in competitions:
            comp_date = datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S')
            if comp_date < datetime.now():
                past_comp = comp
                break
        
        if not past_comp:
            pytest.skip("Aucune compétition passée dans les données")
        
        # Tenter d'accéder à la page de réservation
        response = client.get(f'/book/{past_comp["name"]}/{clubs[0]["name"]}')
        
        # Le système devrait empêcher l'accès ou afficher un message d'erreur
        assert response.status_code in [302, 200]  # Redirection ou page avec erreur
        
        # Si c'est une page, elle ne devrait pas contenir le formulaire de réservation
        if response.status_code == 200:
            assert b'<form' not in response.data or 'Cette compétition est terminée'.encode('utf-8') in response.data
    
    def test_cannot_book_past_competition_via_post(self, client):
        """Test : impossible de réserver via POST pour une compétition passée"""
        if not clubs or not competitions:
            pytest.skip("Pas de données disponibles")
        
        # Trouver une compétition passée
        past_comp = None
        for comp in competitions:
            comp_date = datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S')
            if comp_date < datetime.now():
                past_comp = comp
                break
        
        if not past_comp:
            pytest.skip("Aucune compétition passée")
        
        # Tenter une réservation directe via POST
        response = client.post('/purchasePlaces',
                              data={
                                  'competition': past_comp['name'],
                                  'club': clubs[0]['name'],
                                  'places': '1'
                              },
                              follow_redirects=True)
        
        # Devrait avoir un message d'erreur, pas de confirmation
        assert b'Great-booking complete!' not in response.data
        # Devrait avoir un message indiquant que c'est impossible
        assert b'past' in response.data.lower() or 'terminée'.encode('utf-8') in response.data.lower()
    
    def test_past_competition_not_bookable_in_welcome(self, client):
        """Test : les compétitions passées ne devraient pas avoir de lien 'Book Places'"""
        if not clubs:
            pytest.skip("Pas de clubs disponibles")
        
        # Se connecter
        response = client.post('/showSummary',
                              data={'email': clubs[0]['email']},
                              follow_redirects=True)
        
        assert response.status_code == 200
        
        # Parser le HTML pour vérifier les compétitions passées
        html = response.data.decode('utf-8')
        
        # Les compétitions passées devraient être visibles mais sans lien de réservation
        for comp in competitions:
            comp_date = datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S')
            if comp_date < datetime.now():
                # La compétition devrait être listée
                assert comp['name'] in html
                # Mais PAS avec un lien de réservation actif
                # Vérifier qu'il n'y a pas de lien book pour cette compétition
                book_link = f"book/{comp['name']}"
                if book_link in html:
                    # Si le lien existe, il devrait être désactivé ou avoir une classe spéciale
                    pytest.fail(f"La compétition passée {comp['name']} a un lien de réservation actif")
    
    def test_future_competition_still_bookable(self, client):
        """Test : les compétitions futures doivent rester réservables"""
        if not clubs or not competitions:
            pytest.skip("Pas de données disponibles")
        
        # Trouver une compétition future
        future_comp = None
        for comp in competitions:
            comp_date = datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S')
            if comp_date > datetime.now() and int(comp['numberOfPlaces']) > 0:
                future_comp = comp
                break
        
        if not future_comp:
            pytest.skip("Aucune compétition future disponible")
        
        # Accéder à la page de réservation
        response = client.get(f'/book/{future_comp["name"]}/{clubs[0]["name"]}')
        
        # Devrait fonctionner normalement
        assert response.status_code == 200
        assert b'<form' in response.data
        assert b'How many places?' in response.data


@pytest.mark.unit
@pytest.mark.issue5
class TestPastCompetitionsLogic:
    """Tests unitaires pour la logique de vérification des dates"""
    
    def test_is_competition_past(self):
        """Test unitaire : vérifier si une compétition est passée"""
        # Dates de test
        past_date = '2020-01-01 10:00:00'
        future_date = '2030-12-31 23:59:59'
        
        # Fonction helper à tester (à ajouter dans server.py)
        def is_competition_past(date_str):
            """Vérifie si une compétition est passée"""
            comp_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            return comp_date < datetime.now()
        
        # Tests
        assert is_competition_past(past_date) == True
        assert is_competition_past(future_date) == False
    
    def test_filter_bookable_competitions(self):
        """Test unitaire : filtrer les compétitions réservables"""
        test_competitions = [
            {'name': 'Past', 'date': '2020-01-01 10:00:00', 'numberOfPlaces': '10'},
            {'name': 'Future', 'date': '2030-12-31 10:00:00', 'numberOfPlaces': '10'},
            {'name': 'No Places', 'date': '2030-06-01 10:00:00', 'numberOfPlaces': '0'},
        ]
        
        def get_bookable_competitions(competitions):
            """Retourne seulement les compétitions réservables"""
            bookable = []
            for comp in competitions:
                comp_date = datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S')
                if comp_date > datetime.now() and int(comp['numberOfPlaces']) > 0:
                    bookable.append(comp)
            return bookable
        
        bookable = get_bookable_competitions(test_competitions)
        
        # Seule 'Future' devrait être réservable
        assert len(bookable) == 1
        assert bookable[0]['name'] == 'Future'
    
    def test_date_validation_edge_cases(self):
        """Test unitaire : cas limites de validation de dates"""
        # Tester avec différents formats et cas limites
        now = datetime.now()
        
        # Une minute dans le passé
        just_past = (now - timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Une minute dans le futur
        just_future = (now + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
        
        def is_bookable(date_str):
            comp_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            return comp_date > datetime.now()
        
        assert is_bookable(just_past) == False
        assert is_bookable(just_future) == True


@pytest.mark.integration
@pytest.mark.issue5
class TestPastCompetitionsIntegration:
    """Tests d'intégration pour le workflow complet"""
    
    def test_complete_workflow_with_past_competition(self, client):
        """Test d'intégration : workflow complet avec compétition passée"""
        if not clubs:
            pytest.skip("Pas de données")
        
        # 1. Se connecter
        response = client.post('/showSummary',
                              data={'email': clubs[0]['email']},
                              follow_redirects=True)
        assert response.status_code == 200
        
        # 2. Vérifier que les compétitions passées sont marquées différemment
        html = response.data.decode('utf-8')
        
        # 3. Pour chaque compétition, vérifier le bon comportement
        for comp in competitions:
            comp_date = datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S')
            if comp_date < datetime.now():
                # Compétition passée : pas de lien ou message approprié
                if f'/book/{comp["name"]}' in html:
                    # Si le lien existe, tenter de l'utiliser
                    book_response = client.get(f'/book/{comp["name"]}/{clubs[0]["name"]}')
                    # Devrait être bloqué ou redirigé
                    assert book_response.status_code != 200 or 'terminée'.encode('utf-8') in book_response.data.lower()
            else:
                # Compétition future : devrait fonctionner
                if int(comp['numberOfPlaces']) > 0:
                    assert comp['name'] in html  # Devrait être listé