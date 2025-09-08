import pytest
import sys
import os

# Ajouter le dossier parent au path pour importer server
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from server import app

@pytest.fixture
def client():
    """Client de test Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client