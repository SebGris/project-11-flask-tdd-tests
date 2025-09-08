import sys
import os
import pytest

# Ajouter le répertoire parent au path Python pour importer server
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

@pytest.fixture
def client():
    """Client de test Flask basique - chaque test gère ses propres données"""
    from server import app
    
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client