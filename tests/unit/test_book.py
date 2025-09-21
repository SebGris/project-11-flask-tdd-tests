import pytest


@pytest.mark.parametrize(
    "competitions, clubs, route, expected_status, expected_content",
    [
        # Test avec club invalide
        (
            [
                {
                    'name': 'Test Competition',
                    'date': '2025-06-01 10:00:00',
                    'numberOfPlaces': '10'
                }
            ],
            [],  # Aucun club
            '/book/Test Competition/Invalid Club',
            302,  # Redirection
            None
        ),
        # Test avec compétition invalide
        (
            [],  # Aucune compétition
            [{'name': 'Test Club', 'email': 'test@club.com', 'points': '10'}],
            '/book/Invalid Competition/Test Club',
            302,  # Redirection
            None
        ),
        # Test avec entités valides
        (
            [
                {
                    'name': 'Test Competition',
                    'date': '2025-06-01 10:00:00',
                    'numberOfPlaces': '15'
                }
            ],
            [{'name': 'Test Club', 'email': 'test@club.com', 'points': '10'}],
            '/book/Test Competition/Test Club',
            200,  # Success
            [b'Test Competition', b'Places available: 15', b'How many places?']
        )
    ]
)
def test_book_route(
    client,
    monkeypatch,
    competitions,
    clubs,
    route,
    expected_status,
    expected_content
):
    """Tester la route book avec différentes combinaisons d'entités"""
    monkeypatch.setattr('server.competitions', competitions)
    monkeypatch.setattr('server.clubs', clubs)

    response = client.get(route)
    assert response.status_code == expected_status

    if expected_status == 302:
        assert response.location == '/'
    elif expected_content:
        for content in expected_content:
            assert content in response.data
