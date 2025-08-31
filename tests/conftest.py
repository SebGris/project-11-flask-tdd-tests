import sys
import os
import pytest

# Ajouter le répertoire parent au path Python pour importer server
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from server import app

@pytest.fixture
def client():
    """Client de test Flask pour les tests d'intégration"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def past_competition():
    """Fixture pour une compétition passée (Spring Festival)"""
    return {
        'name': 'Spring Festival',
        'date': '2020-03-27 10:00:00',
        'numberOfPlaces': '25'
    }

@pytest.fixture
def future_competition():
    """Fixture pour une compétition future (Fall Classic)"""
    return {
        'name': 'Fall Classic', 
        'date': '2025-10-22 13:00:00',
        'numberOfPlaces': '15'
    }