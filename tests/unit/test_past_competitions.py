"""
Tests UNITAIRES pour l'issue #5 : Validation des dates de compétition
Fichier : tests/unit/test_past_competitions.py
"""
import pytest
from datetime import datetime
from unittest.mock import patch
from server import is_competition_past


@pytest.mark.unit
class TestIsCompetitionPast:
    """Tests unitaires pour la fonction is_competition_past"""
    
    def test_past_competition_returns_true(self, past_competition):
        """Test: Retourne True pour une compétition passée"""
        result = is_competition_past(past_competition)
        assert result is True
    
    def test_future_competition_returns_false(self, future_competition):
        """Test: Retourne False pour une compétition future"""
        with patch('server.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 8, 31, 12, 0, 0)
            mock_datetime.strptime = datetime.strptime
            
            result = is_competition_past(future_competition)
            assert result is False