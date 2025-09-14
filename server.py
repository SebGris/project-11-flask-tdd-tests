import json
from flask import Flask,render_template,request,redirect,flash,url_for
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


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    for comp in competitions:
        comp_date = datetime.strptime(comp['date'], "%Y-%m-%d %H:%M:%S")
        comp['is_past'] = comp_date < datetime.now()
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])
    
    # NOUVEAU : Vérifier si la compétition est passée
    competition_date = datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S")
    if competition_date < datetime.now():
        flash('Cannot book places for past competitions')
        return render_template('welcome.html', club=club, competitions=competitions)
    
    # Validations existantes (si vous les avez déjà)
    if placesRequired > 12:
        flash('Cannot book more than 12 places at once')
        return render_template('welcome.html', club=club, competitions=competitions)
    
    if placesRequired > int(club['points']):
        flash(f"Not enough points. You have {club['points']} points.")
        return render_template('welcome.html', club=club, competitions=competitions)
    
    # Déduction des points et places
    club['points'] = str(int(club['points']) - placesRequired)
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)

# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))