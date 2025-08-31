import json
from flask import Flask,render_template,request,redirect,flash,url_for
from datetime import datetime

def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


def find_club_by_email(email, clubs_list):
    """Find a club by email address.
    
    Args:
        email: Email address to search for
        clubs_list: List of club dictionaries
        
    Returns:
        dict or None: The found club or None if not found
    """
    return next((club for club in clubs_list if club['email'] == email), None)


def validate_email_input(email):
    """Validate that email is present and not empty.
    
    Args:
        email: Email string to validate
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    return bool(email and str(email).strip())


def is_competition_past(competition):
    """Vérifie si une compétition est passée."""
    competition_date = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
    return competition_date < datetime.now()


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    # Get email from form
    email = request.form.get('email')
    
    # Check if email is provided
    if not email:
        flash("Veuillez entrer une adresse e-mail.")
        return redirect(url_for('index'))
    
    # Try to find the club with this email
    matching_clubs = [club for club in clubs if club['email'] == email]
    
    # Check if club exists
    if not matching_clubs:
        flash("Désolé, cette adresse e-mail est introuvable.")
        return redirect(url_for('index'))
    
    # Get the club (we know it exists now)
    club = matching_clubs[0]

    competitions_with_status = []
    for comp in competitions:
        comp_copy = comp.copy()
        comp_copy['is_past'] = is_competition_past(comp)
        competitions_with_status.append(comp_copy)
    
    return render_template('welcome.html', 
                         club=club, 
                         competitions=competitions_with_status)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]

    if is_competition_past(foundCompetition):
        flash("Cannot book places for past competitions")
        return redirect(url_for('index'))
    
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    
    if is_competition_past(competition):
        flash("Cannot book places for past competitions")
        return redirect(url_for('index'))
    
    placesRequired = int(request.form['places'])
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))