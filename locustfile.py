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

    @task(3)
    def view_competitions(self):
        """Test < 5s"""
        with self.client.post('/showSummary',
                              data={'email': self.current_email},
                              catch_response=True,
                              name="View Competitions") as response:
            if response.elapsed.total_seconds() > 5:
                response.failure(
                    f"Temps > 5s: {response.elapsed.total_seconds()}s"
                )

    @task(4)
    def book_places(self):
        """Test réservation < 2s - Version simple"""
        with self.client.post('/purchasePlaces',
                              data={
                                'competition': 'Spring Festival',
                                'club': self.current_club,
                                'places': '1'
                              },
                              catch_response=True,
                              name="Book Places") as response:
            # Simple : accepter si < 2s, peu importe le résultat
            if response.elapsed.total_seconds() > 2:
                response.failure("Temps > 2s")
            else:
                response.success()

    @task(1)
    def view_points_board(self):
        """Test < 5s"""
        with self.client.get('/points',
                             catch_response=True,
                             name="Points Board") as response:
            if response.elapsed.total_seconds() > 5:
                response.failure("Temps > 5s")
