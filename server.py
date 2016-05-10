"""Hackbright Project"""

from flask import Flask, render_template, redirect, request, flash, session
from jinja2 import StrictUndefined
from model import connect_to_db, db, User, Log, Location
from datetime import datetime
import os

app = Flask(__name__)

#for debug toolbar
app.secret_key = 'ABC'
google_api = os.environ['GOOGLE_LOC_API']
google_location_api = "https://maps.googleapis.com/maps/api/js?key="+google_api+"&libraries=places&callback=initMap"

app.jinja_env.undefined = StrictUndefined


@app.route('/')
def homepage():

    try: 
        session['user']
        return redirect('/profile/'+session['user'])
    except:
        return render_template('homepage.html')

@app.route('/signup')
def signup():

    return render_template('signup.html')

@app.route('/check-login', methods=['POST'])
def check_login():
    """Checks to see if username and password match account"""

    username = request.form.get('username')
    password = request.form.get('password')
    session['user'] = username


    try:
        user = User.query.filter(User.username == username).one()
        if user.username == username and user.password == password:
            session['user'] = username
            session['home_lat'] = user.home_lat 
            session['home_long'] = user.home_long
            return 'True'
        else: 
            return 'False'

    except:
        return 'False'

@app.route('/logout')
def logout():

    flash('Successfully logged out')
    session.pop('user')
    return redirect('/')


@app.route('/create-profile', methods=['POST'])
def check_signup_pw():
    """Checks to see if passwords match"""

    fname = request.form.get('fname') 
    lname = request.form.get('lname')
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('pw')

    user = User(email=email, username=username, 
                password=password, fname=fname, lname=lname)

    db.session.add(user)
    db.session.commit()

    session['user'] = username
    print session['user']
    return render_template('profile.html', fname=fname, lname=lname,
                            email=email, username=username, 
                            google_location_api=google_location_api)



@app.route('/set-home', methods=['POST'])
def set_home():
    """Sets user home location"""

    print "I got here"

    home_lat = request.form.get('lat')
    home_long = request.form.get('long')

    print "I retrieved home lat and long"

    user = User.query.filter(User.email == session['user']).one()

    print "I found a user"

    setattr(user, 'home_lat', home_lat)

    print "I set home lat"

    setattr(user, 'home_long', home_long)

    print "I set home long"


    db.session.commit()

    print "I totally committed"

    user = User.query.filter(User.email == session['user']).one()

    session['home_lat'] = home_lat 
    session['home_long'] = home_long

    return "True"

@app.route('/profile/<username>')
def profile_page(username):
    """Render profile page"""

    current_date = datetime.now().strftime('%A, %B %d, %Y')

    user = User.query.filter(User.username == username).one() 

    user_logs = Log.query.filter(Log.user_id == user.user_id)

    return render_template('profile_page.html', username=username, 
                        current_date=current_date, user_logs=user_logs)


@app.route('/profile/<username>/add-location')
def add_location(username):

    return render_template('add_location.html', 
                    google_location_api=google_location_api)

@app.route('/log-new-location', methods=['POST'])
def log_new_location():
    """take input, log new location"""

    latitude = request.form.get('lat')
    longitude = request.form.get('long')
    address = request.form.get('address')
    location_id = request.form.get('location_id')
    title = request.form.get('title')
    arrived = request.form.get('arrival')
    departed = request.form.get('departure')
    visit_date = request.form.get('date')
    created_at = datetime.now()
    comments = request.form.get('comments')

    print "I have finished this stuff"

    user = User.query.filter(User.username == session['user']).one()
    print "I got this user", user


    print location_id, latitude, longitude, address
    print type(latitude)
    print type(longitude)

    location = Location(location_id=location_id, latitude=latitude,
                        longitude=longitude, address=address)

    
    db.session.add(location)
    db.session.commit()
    print "I added a location"

    log = Log(user_id=user.user_id, location_id=location_id, 
            created_at=created_at, visit_date=visit_date, arrived=arrived,
            departed=departed, comments=comments, title=title)

    db.session.add(log)
    db.session.commit()
    print "I created a log"

    return "True"
    return


###################

if __name__ == '__main__':

    connect_to_db(app)

    app.run()