import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for

MAX_PLACES = 12  # Limite de réservation par compétition


def load_clubs():
    """Charger les clubs depuis le fichier JSON"""
    with open('clubs.json') as c:
        list_of_clubs = json.load(c)['clubs']
        return list_of_clubs


def load_competitions():
    """Charger les compétitions depuis le fichier JSON"""
    with open('competitions.json') as comps:
        list_of_competitions = json.load(comps)['competitions']
        return list_of_competitions


def load_bookings():
    """Charger les réservations depuis le fichier JSON"""
    try:
        with open('bookings.json') as b:
            bookings_list = json.load(b)['bookings']
            bookings_dict = {}
            for booking in bookings_list:
                key = (booking['club'], booking['competition'])
                # Si c'est une liste de bookings, additionner
                if key in bookings_dict:
                    bookings_dict[key] += booking['places']
                else:
                    bookings_dict[key] = booking['places']
            return bookings_dict
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_clubs(clubs):
    """Sauvegarder les clubs dans le fichier JSON"""
    with open('clubs.json', 'w') as f:
        json.dump({'clubs': clubs}, f, indent=4)


def save_competitions(competitions):
    """Sauvegarder les compétitions dans le fichier JSON"""
    with open('competitions.json', 'w') as f:
        json.dump({'competitions': competitions}, f, indent=4)


def save_bookings(bookings_dict):
    """Sauvegarder les réservations dans le fichier JSON"""
    bookings_list = []
    for (club, competition), total_places in bookings_dict.items():
        bookings_list.append({
            'club': club,
            'competition': competition,
            'places': total_places,
            'timestamp': datetime.now().isoformat()
        })

    with open('bookings.json', 'w') as f:
        json.dump({'bookings': bookings_list}, f, indent=4)


def prepare_competitions_for_display():
    """Ajoute le flag is_past à chaque compétition pour l'affichage"""
    for comp in competitions:
        comp_date = datetime.strptime(comp['date'], "%Y-%m-%d %H:%M:%S")
        comp['is_past'] = comp_date < datetime.now()


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = load_competitions()
clubs = load_clubs()
bookings = load_bookings()


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
    prepare_competitions_for_display()
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
        prepare_competitions_for_display()
        return render_template('welcome.html',
                               club=club,
                               competitions=competitions)

    # Validations métier
    error_message = validate_booking(competition, club, places_required)
    if error_message:
        flash(error_message)
        prepare_competitions_for_display()
        return render_template('welcome.html',
                               club=club,
                               competitions=competitions)

    # Traitement de la réservation
    process_booking(competition, club, places_required)

    save_clubs(clubs)
    save_competitions(competitions)
    save_bookings(bookings)

    flash('Great-booking complete!')
    prepare_competitions_for_display()
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
        return "Cannot book places for past competitions."

    # 2. Vérifier le nombre minimum de places
    if places_required <= 0:
        return "You must book at least 1 place."

    # 3. Vérifier les points disponibles
    if places_required > int(club['points']):
        return f"Not enough points. You have {club['points']} points available"

    # 4. Vérifier les places disponibles dans la compétition
    if places_required > int(competition['numberOfPlaces']):
        places_left = competition['numberOfPlaces']
        return f"Not enough places available. Only {places_left} places left"

    # Validation de la limite de 12 places
    booking_key = (club['name'], competition['name'])
    already_booked = bookings.get(booking_key, 0)
    total_would_be = already_booked + places_required

    if places_required > MAX_PLACES or total_would_be > MAX_PLACES:
        if places_required > MAX_PLACES:
            return f"Cannot book more than {MAX_PLACES} places at once"
        else:
            return (
                f"Cannot book more than {MAX_PLACES} places "
                "in total for this competition"
            )

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
