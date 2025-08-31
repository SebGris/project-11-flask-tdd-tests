# tests/unit/test_email_functions.py
"""
Tests unitaires pour les fonctions email de server.py
"""
import sys
import os
import pytest

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from server import find_club_by_email, validate_email_input


@pytest.mark.unit
class TestFindClubByEmail:
    """Tests unitaires pour find_club_by_email"""
    
    def test_find_existing_club(self):
        """Test: trouver un club qui existe"""
        # Arrange
        clubs = [
            {'name': 'Test Club', 'email': 'test@example.com', 'points': '10'},
            {'name': 'Other Club', 'email': 'other@example.com', 'points': '15'}
        ]
        
        # Act
        result = find_club_by_email('test@example.com', clubs)
        
        # Assert
        assert result is not None
        assert result['name'] == 'Test Club'
        assert result['email'] == 'test@example.com'

    def test_find_nonexistent_club(self):
        """Test: retourne None si le club n'existe pas"""
        # Arrange
        clubs = [
            {'name': 'Test Club', 'email': 'test@example.com', 'points': '10'}
        ]
        
        # Act
        result = find_club_by_email('notfound@example.com', clubs)
        
        # Assert
        assert result is None


@pytest.mark.unit
class TestValidateEmailInput:
    """Tests unitaires pour validate_email_input"""
    
    def test_valid_email(self):
        """Test: email valide"""
        # Act
        is_valid = validate_email_input('test@example.com')
        
        # Assert
        assert is_valid is True