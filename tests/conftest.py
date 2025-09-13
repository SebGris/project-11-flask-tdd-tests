import pytest


@pytest.fixture
def client():
    """Client de test Flask basique - chaque test gère ses propres données"""
    from server import app
    
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client