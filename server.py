"""
Flask application for GUDLFT competition booking system.
"""
import json
from flask import Flask, render_template, request, redirect, flash, url_for


def load_clubs():
    """Load clubs data from JSON file.

    Returns:
        list: List of club dictionaries
    """
    with open('clubs.json') as clubs_file:
        clubs_list = json.load(clubs_file)['clubs']
        return clubs_list


def load_competitions():
    """Load competitions data from JSON file.

    Returns:
        list: List of competition dictionaries
    """
    with open('competitions.json') as competitions_file:
        competitions_list = json.load(competitions_file)['competitions']
        return competitions_list


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = load_competitions()
clubs = load_clubs()


@app.route('/')
def index():
    """Display the home page with login form.

    Returns:
        str: Rendered HTML template for index page
    """
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def show_summary():
    """Display summary page after login.

    Returns:
        str: Rendered HTML template for welcome page or redirect to index
    """
    email = request.form.get('email')
    
    # Cas 1 : Email manquant ou vide
    if not email:
        flash("Veuillez saisir une adresse e-mail.")
        return redirect(url_for('index'))
    
    # Rechercher le club
    club_list = [
        club for club in clubs
        if club['email'] == email
    ]

    # Cas 2 : Email fourni mais inexistant
    if not club_list:
        flash("Désolé, cette adresse e-mail est introuvable.")
        return redirect(url_for('index'))

    club = club_list[0]
    return render_template('welcome.html', club=club, competitions=competitions)

@app.route('/book/<competition>/<club>')
def book(competition, club):
    """Display booking page for a specific competition and club.

    Args:
        competition (str): Name of the competition
        club (str): Name of the club

    Returns:
        str: Rendered HTML template for booking page
    """
    found_club = [c for c in clubs if c['name'] == club]
    found_competition = [
        c for c in competitions
        if c['name'] == competition
    ]

    if found_club and found_competition:
        return render_template(
            'booking.html',
            club=found_club[0],
            competition=found_competition[0]
        )
    else:
        flash("Something went wrong-please try again")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions
        )


@app.route('/purchasePlaces', methods=['POST'])
def purchase_places():
    """Process the purchase of competition places.

    Returns:
        str: Rendered HTML template for welcome page with confirmation
    """
    competition = [
        c for c in competitions
        if c['name'] == request.form['competition']
    ][0]

    club = [
        c for c in clubs
        if c['name'] == request.form['club']
    ][0]

    places_required = int(request.form['places'])
    competition['numberOfPlaces'] = (
        int(competition['numberOfPlaces']) - places_required
    )

    flash('Great-booking complete!')
    return render_template(
        'welcome.html',
        club=club,
        competitions=competitions
    )


# TODO: Add route for points display


@app.route('/logout')
def logout():
    """Log out the user and redirect to home page.

    Returns:
        Response: Redirect to index page
    """
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
