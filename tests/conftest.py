"""
Configuration pytest et fixtures partagées pour tous les tests
"""
import sys
import os
import pytest

# Ajouter le répertoire parent au path Python pour importer server
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from server import app


@pytest.fixture
def client():
    """Client de test Flask pour les tests fonctionnels.
    
    Cette fixture est automatiquement disponible dans tous les tests.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_clubs():
    """Données de clubs pour les tests.
    
    Returns:
        list: Liste de clubs de test avec différents cas
    """
    return [
        {
            'name': 'Test Club 1',
            'email': 'test1@example.com',
            'points': '15'
        },
        {
            'name': 'Test Club 2',
            'email': 'test2@example.com',
            'points': '20'
        },
        {
            'name': 'Test Club 3',
            'email': 'Test@Example.com',  # Email avec casse mixte
            'points': '10'
        },
        {
            'name': 'Club Low Points',
            'email': 'low@example.com',
            'points': '2'  # Peu de points pour tester les limites
        }
    ]


@pytest.fixture
def mock_competitions():
    """Données de compétitions pour les tests.
    
    Returns:
        list: Liste de compétitions avec différents états
    """
    return [
        {
            'name': 'Test Competition Future',
            'date': '2025-12-01 10:00:00',
            'numberOfPlaces': '25'
        },
        {
            'name': 'Test Competition Past',
            'date': '2024-01-01 10:00:00',
            'numberOfPlaces': '10'
        },
        {
            'name': 'Test Competition Full',
            'date': '2025-11-15 14:00:00',
            'numberOfPlaces': '0'
        },
        {
            'name': 'Test Competition Limited',
            'date': '2025-10-20 09:00:00',
            'numberOfPlaces': '3'  # Peu de places
        }
    ]


@pytest.fixture
def valid_club_data(mock_clubs):
    """Retourne les données d'un club valide pour les tests.
    
    Args:
        mock_clubs: Fixture des clubs mock
        
    Returns:
        dict: Données d'un club valide
    """
    return mock_clubs[0]


@pytest.fixture
def valid_competition_data(mock_competitions):
    """Retourne les données d'une compétition valide pour les tests.
    
    Args:
        mock_competitions: Fixture des compétitions mock
        
    Returns:
        dict: Données d'une compétition future valide
    """
    return mock_competitions[0]


@pytest.fixture
def past_competition_data(mock_competitions):
    """Retourne les données d'une compétition passée pour les tests.
    
    Args:
        mock_competitions: Fixture des compétitions mock
        
    Returns:
        dict: Données d'une compétition passée
    """
    return mock_competitions[1]


@pytest.fixture(autouse=True)
def reset_app_state():
    """Reset l'état de l'application avant chaque test.
    
    Cette fixture s'exécute automatiquement avant chaque test
    pour garantir l'isolation des tests.
    """
    # Si vous avez des variables globales à réinitialiser
    # ou des états à nettoyer, faites-le ici
    yield
    # Nettoyage après le test si nécessaire


# Marqueurs personnalisés pour organiser les tests
def pytest_configure(config):
    """Configure les marqueurs personnalisés pour pytest."""
    config.addinivalue_line(
        "markers", "unit: Tests unitaires rapides et isolés"
    )
    config.addinivalue_line(
        "markers", "functional: Tests fonctionnels de bout en bout"
    )
    config.addinivalue_line(
        "markers", "integration: Tests d'intégration complets"
    )
    config.addinivalue_line(
        "markers", "slow: Tests lents (plus de 1 seconde)"
    )
    config.addinivalue_line(
        "markers", "issue1: Tests pour l'issue #1 (email validation)"
    )
    config.addinivalue_line(
        "markers", "issue2: Tests pour l'issue #2 (booking overflow)"
    )
    config.addinivalue_line(
        "markers", "issue3: Tests pour l'issue #3 (points display)"
    )
    config.addinivalue_line(
        "markers", "issue4: Tests pour l'issue #4 (points update)"
    )
    config.addinivalue_line(
        "markers", "issue5: Tests pour l'issue #5 (past competitions)"
    )
    config.addinivalue_line(
        "markers", "issue6: Tests pour l'issue #6 (12 places limit)"
    )
    config.addinivalue_line(
        "markers", "issue7: Tests pour l'issue #7 (points limit)"
    )