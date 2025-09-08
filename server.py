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


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    email = request.form['email']
    # Chercher le club avec une meilleure gestion d'erreur
    club = next((c for c in clubs if c['email'] == email), None)
    
    if not club:
        flash("Sorry, that email wasn't found.")
        return redirect(url_for('index'))
    
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
        
    # Validation 1: Vérifier si la compétition est passée
    competition_date = datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S")
    if competition_date < datetime.now():
        flash('Cannot book places for past competitions')
        return render_template('welcome.html', club=club, competitions=competitions)
    
    # Validation 2: limite 12 places
    if placesRequired > 12:
        flash('Cannot book more than 12 places at once')
        return render_template('welcome.html', club=club, competitions=competitions)
    
    # Validation 3: vérifier les points disponibles
    if placesRequired > int(club['points']):
        flash(f"Not enough points. You have {club['points']} points.")
        return render_template('welcome.html', club=club, competitions=competitions)
    
    # Validation 4: vérifier les places disponibles dans la compétition
    if placesRequired > int(competition['numberOfPlaces']):
        flash(f"Not enough places available. Only {competition['numberOfPlaces']} places left.")
        return render_template('welcome.html', club=club, competitions=competitions)
    
    # Déduction des points et places
    current_points = int(club['points'])
    new_points = current_points - placesRequired
    club['points'] = str(new_points)

    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)

# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))