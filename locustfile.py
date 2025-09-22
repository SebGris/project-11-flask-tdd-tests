from locust import HttpUser, task, between
import random


class GUDLFTUser(HttpUser):
    """Simule un secrétaire de club utilisant l'application"""
    wait_time = between(1, 3)

    def on_start(self):
        """Setup initial"""
        self.users = [
            ('john@simplylift.co', 'Simply Lift'),
            ('admin@irontemple.com', 'Iron Temple'),
            ('kate@shelifts.co', 'She Lifts')
        ]
        self.current_email, self.current_club = random.choice(self.users)
        self.login()

    def login(self):
        """Connexion initiale"""
        self.client.post('/showSummary',
                         data={'email': self.current_email},
                         name="Login")

    @task()
    def view_competitions(self):
        """Affichage des compétitions"""
        self.client.post('/showSummary',
                         data={'email': self.current_email},
                         name="View Competitions")

    @task()
    def book_places(self):
        """Réservation de places"""
        self.client.post('/purchasePlaces',
                         data={
                            'competition': 'Spring Festival',
                            'club': self.current_club,
                            'places': '1'
                         },
                         name="Book Places")

    @task()
    def view_points_board(self):
        """Tableau des points"""
        self.client.get('/points', name="Points Board")
