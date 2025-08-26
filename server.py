import json
from datetime import datetime
from flask import Flask,render_template,request,redirect,flash,url_for


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

def is_competition_past(competition_date_str):
    """Check if a competition date is in the past.
    
    Args:
        competition_date_str: Date string in format 'YYYY-MM-DD HH:MM:SS'
        
    Returns:
        bool: True if competition is past, False otherwise
    """
    competition_date = datetime.strptime(competition_date_str, '%Y-%m-%d %H:%M:%S')
    return competition_date < datetime.now()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
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
    return render_template('welcome.html',
                           club=club,
                           competitions=competitions,
                           is_past=is_competition_past)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    selected_club = [c for c in clubs if c['name'] == club][0]
    selected_competition = [c for c in competitions if c['name'] == competition][0]
    
    if selected_club and selected_competition:
        # FIX ISSUE #5: Check if competition is in the past
        if is_competition_past(selected_competition['date']):
            flash("Sorry, this competition has already taken place and cannot be booked.")
            return render_template('welcome.html', 
                                 club=selected_club, 
                                 competitions=competitions,
                                 is_past=is_competition_past)
        
        return render_template('booking.html',club=selected_club,competition=selected_competition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', 
                             club=club, 
                             competitions=competitions,
                             is_past=is_competition_past)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    
    # FIX ISSUE #5: Check if competition is in the past before allowing purchase
    if is_competition_past(competition['date']):
        flash("Sorry, this competition has already taken place and cannot be booked.")
        return render_template('welcome.html', 
                             club=club, 
                             competitions=competitions,
                             is_past=is_competition_past)
    
    placesRequired = int(request.form['places'])
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', 
                         club=club, 
                         competitions=competitions,
                         is_past=is_competition_past)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))