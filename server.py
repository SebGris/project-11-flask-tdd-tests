import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime, timedelta


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

# Ajouter une compétition de test dans le futur (sans toucher au JSON)
future_datetime = datetime.now() + timedelta(days=30)
future_date = future_datetime.strftime("%Y-%m-%d %H:%M:%S")
competitions.append({
    'name': 'Test Future Competition',
    'date': future_date,
    'numberOfPlaces': '15'
})

# Dictionnaire pour tracker les réservations
bookings = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form['email']
    # Chercher le club avec une meilleure gestion d'erreur
    club = next((c for c in clubs if c['email'] == email), None)

    if not club:
        flash("Sorry, that email wasn't found.")
        return redirect(url_for('index'))

    for comp in competitions:
        comp_date = datetime.strptime(comp['date'], "%Y-%m-%d %H:%M:%S")
        comp['is_past'] = comp_date < datetime.now()

    return render_template('welcome.html',
                           club=club,
                           competitions=competitions)


def validate_entities(club, competition):
    """Valide l'existence du club et de la compétition."""
    if not club:
        flash("Club introuvable.")
        return False
    if not competition:
        flash("Compétition introuvable.")
        return False
    return True


@app.route('/book/<competition_name>/<club_name>')
def book(competition_name, club_name):
    # Recherche du club et de la compétition
    club = next((c for c in clubs if c['name'] == club_name), None)
    competition = next(
        (c for c in competitions if c['name'] == competition_name),
        None
    )

    if not validate_entities(club, competition):
        return redirect(url_for('index'))

    # Affichage de la page de réservation
    return render_template('booking.html', club=club, competition=competition)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    # Récupération des données du formulaire
    competition_name = request.form.get('competition')
    club_name = request.form.get('club')

    # Recherche des entités
    competition = next(
        (c for c in competitions if c['name'] == competition_name),
        None
    )
    club = next((c for c in clubs if c['name'] == club_name), None)

    if not validate_entities(club, competition):
        return redirect(url_for('index'))

    # Conversion et validation du nombre de places
    try:
        places_required = int(request.form.get('places', 0))
    except ValueError:
        flash("Nombre de places invalide.")
        return render_template('welcome.html',
                               club=club,
                               competitions=competitions)

    # Validations métier
    error_message = validate_booking(competition, club, places_required)
    if error_message:
        flash(error_message)
        return render_template('welcome.html',
                               club=club,
                               competitions=competitions)

    # Traitement de la réservation
    process_booking(competition, club, places_required)

    # Sauvegarde des modifications dans les fichiers JSON (sauf en mode test)
    if not app.config.get('TESTING', False):
        with open('clubs.json', 'w') as f:
            json.dump({'clubs': clubs}, f, indent=4)
        with open('competitions.json', 'w') as f:
            json.dump({'competitions': competitions}, f, indent=4)

    flash('Great-booking complete!')
    return render_template('welcome.html',
                           club=club,
                           competitions=competitions)


def validate_booking(competition, club, places_required):
    """Valide une réservation et retourne un message d'erreur si invalide.

    Args:
        competition: Dictionnaire de la compétition
        club: Dictionnaire du club
        places_required: Nombre de places demandées

    Returns:
        str: Message d'erreur ou None si valide
    """

    # 1. Vérifier si la compétition est passée
    competition_date = datetime.strptime(
        competition['date'],
        "%Y-%m-%d %H:%M:%S"
    )
    if competition_date < datetime.now():
        return "Cannot book places for past competitions"

    # 2. Vérifier le nombre minimum de places
    if places_required <= 0:
        return "You must book at least 1 place"

    # 3. Vérifier la limite de 12 places
    if places_required > 12:
        return "Cannot book more than 12 places at once"

    # Validation : Limite cumulative de 12 places par club pour la compétition
    booking_key = (club['name'], competition['name'])
    already_booked = bookings.get(booking_key, 0)
    total_would_be = already_booked + places_required
    if total_would_be > 12:
        return "Cannot book more than 12 places in total for this competition"

    # 4. Vérifier les points disponibles
    if places_required > int(club['points']):
        return f"Not enough points. You have {club['points']} points available"

    # 5. Vérifier les places disponibles dans la compétition
    if places_required > int(competition['numberOfPlaces']):
        places_left = competition['numberOfPlaces']
        return f"Not enough places available. Only {places_left} places left"

    return None  # Pas d'erreur


def process_booking(competition, club, places_required):
    """Traite la réservation en mettant à jour les points et les places.

    Args:
        competition: Dictionnaire de la compétition (modifié en place)
        club: Dictionnaire du club (modifié en place)
        places_required: Nombre de places à réserver
    """

    # Déduction des points
    current_points = int(club['points'])
    club['points'] = str(current_points - places_required)

    # Déduction des places (garder en string pour cohérence avec JSON)
    current_places = int(competition['numberOfPlaces'])
    competition['numberOfPlaces'] = str(current_places - places_required)

    # Mise à jour des réservations cumulées
    booking_key = (club['name'], competition['name'])
    bookings[booking_key] = bookings.get(booking_key, 0) + places_required


@app.route('/points')
def display_points():
    """Affichage public du tableau des points"""
    return render_template('points.html', clubs=clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
