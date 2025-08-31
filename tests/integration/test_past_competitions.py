"""
Tests d'INTÉGRATION pour l'issue #5
Fichier : tests/integration/test_past_competitions.py
"""
import pytest


@pytest.mark.integration
class TestPastCompetitionsBooking:
    """Tests d'intégration pour empêcher les réservations sur compétitions passées"""
    
    def test_cannot_access_booking_page_for_past_competition(self, client):
        """Test: Redirection pour compétition passée"""
        response = client.get('/book/Spring Festival/Simply Lift')
        assert response.status_code == 302
        assert response.location == '/'
    
    def test_flash_message_displays_for_past_competition(self, client):
        """Test: Message flash s'affiche"""
        response = client.get('/book/Spring Festival/Simply Lift', follow_redirects=True)
        assert response.status_code == 200
        assert b"Cannot book places for past competitions" in response.data
    
    def test_can_access_booking_page_for_future_competition(self, client):
        """Test: Accès normal pour compétition future"""
        response = client.get('/book/Fall Classic/Simply Lift')
        assert response.status_code == 200
        assert b"Fall Classic" in response.data