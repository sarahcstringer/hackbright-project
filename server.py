"""Hackbright Project"""

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import connect_to_db, db, User, Log, Location, Type, LocationType 
from datetime import datetime, timedelta
import os
from sqlalchemy import or_, func

app = Flask(__name__)

#for debug toolbar
app.secret_key = 'ABC'
google_api = os.environ['GOOGLE_LOC_API']
global google_location_api
google_location_api = "https://maps.googleapis.com/maps/api/js?key="+google_api+"&libraries=places&callback=initialize"
app.jinja_env.undefined = StrictUndefined

@app.context_processor
def inject_google_api():
    return dict(google_location_api=google_location_api)

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
    date_created = datetime.now()

    user = User(email=email, username=username, 
                password=password, fname=fname, lname=lname,
                date_created=date_created)

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

    home_lat = request.form.get('lat')
    home_long = request.form.get('long')
    home_address = request.form.get('address')

    user = User.query.filter(User.username == session['user']).one()

    setattr(user, 'home_lat', home_lat)
    setattr(user, 'home_long', home_long)
    setattr(user, 'home_address', home_address)

    db.session.commit()

    user = User.query.filter(User.username == session['user']).one()

    session['home_lat'] = home_lat 
    session['home_long'] = home_long

    return "True"

@app.route('/profile/<username>')
def profile_page(username):
    """Render profile page"""

    current_date = datetime.now().strftime('%A, %B %d, %Y')

    date_of_logs = datetime.now().strftime('%Y-%m-%d')

    user = User.query.filter(User.username == username).one() 

    user_logs = Log.query.filter(Log.user_id == user.user_id,
                                Log.visit_date == unicode(date_of_logs)).all()

    return render_template('profile_page.html', 
                            username=username, 
                            user=user,
                            current_date=current_date, 
                            google_location_api=google_location_api)


@app.route('/profile/<username>/add-location')
def add_location(username):

    return render_template('add_location.html', 
                    google_location_api=google_location_api)

@app.route('/profile/<username>/view-locations')
def view_locations(username):

    return render_template('view_locations.html')

@app.route('/log-new-location', methods=['POST'])
def log_new_location():
    """take input, log new location"""

    latitude = request.form.get('lat')
    longitude = request.form.get('long')
    address = request.form.get('address')
    location_id = request.form.get('location_id')
    name = request.form.get('name')
    title = request.form.get('title')
    arrived = request.form.get('arrival')
    departed = request.form.get('departure')
    visit_date = request.form.get('date')
    created_at = datetime.now()
    comments = request.form.get('comments')
    place_types = request.form.get('place_types').split(',')
    website = request.form.get('website')
    if website == None:
        website = 'N/A'
    phone = request.form.get('phone')
    if phone == None:
        phone = 'N/A'

    user = User.query.filter(User.username == session['user']).one()

    location = Location(location_id=location_id, latitude=latitude,
                        longitude=longitude, address=address, name=name,
                        website=website, phone=phone)

    # create location id
    try:
        Location.query.filter(Location.location_id == location.location_id).one()
    except: 
        db.session.add(location)
        db.session.commit()

    # Loop through the list of place type and add those types to the type db
    for l_type in place_types:
        l_type = l_type.replace('[', '')
        l_type = l_type.replace(']', '')
        l_type = l_type.replace('"', '')
        # if the type already exists in the table, don't add it
        try:
            Type.query.filter(Type.type_name == l_type).one()
        # if it doesn't, add it to the table
        except: 
            add_location_type = Type(type_name=l_type)
            db.session.add(add_location_type)
            db.session.commit()

    for l_type in place_types:
        l_type = l_type.replace('[', '')
        l_type = l_type.replace(']', '')
        l_type = l_type.replace('"', '')
        # type should already exist in db now, from above step
        type_obj = Type.query.filter(Type.type_name == l_type).one()
        
        # see if the location-type connection exists in table
        try:
            LocationType.query.filter(LocationType.location_id == location_id & 
                LocationType.type_id == type_obj.type_id).one()
        except:
            type_obj = Type.query.filter(Type.type_name == l_type).one()
            location_type_log = LocationType(location_id=location_id, 
                                            type_id=type_obj.type_id)
            db.session.add(location_type_log)
            db.session.commit()

    # create a log for this location for the user
    log = Log(user_id=user.user_id, location_id=location_id, 
            created_at=created_at, visit_date=visit_date, arrived=arrived,
            departed=departed, comments=comments, title=title)

    db.session.add(log)
    db.session.commit()

    return "True"


@app.route('/load_today')
def load_today():
    """Load today's information"""

    current_date = datetime.now().strftime('%A, %B %d, %Y')
    date_of_logs = datetime.now().strftime('%Y-%m-%d')

    user = User.query.filter(User.username == session['user']).one()

    user_logs = Log.query.filter(Log.user_id == user.user_id,
                                Log.visit_date == unicode(date_of_logs)).all()
    logs = {
        log.log_id: {
            'locationId': log.location_id,
            'visitDate': log.visit_date,
            'arrived': log.arrived,
            'departed': log.departed,
            'comments': log.comments,
            'title': log.title,
            'user': log.user_id,
            'locationLat': log.location.latitude,
            'locationLong': log.location.longitude,
            'log_id': log.log_id
        }
        for log in Log.query.filter(Log.user_id == user.user_id,
                                Log.visit_date == unicode(date_of_logs)).all()}

    info = {'date': current_date,
            'logs': logs}

    return jsonify(info)


@app.route('/change-previous-day', methods=['POST'])
def change_previous_day():
    """Change to show previous day"""

    d = request.form.get('showDate')
    current_date = datetime.strptime(d, '%A, %B %d, %Y')
    previous_day = current_date - timedelta(days=1)
    date_of_logs = previous_day.strftime('%Y-%m-%d')

    user = User.query.filter(User.username == session['user']).one()

    logs = {
        log.log_id: {
            'locationId': log.location_id,
            'visitDate': log.visit_date,
            'arrived': log.arrived,
            'departed': log.departed,
            'comments': log.comments,
            'title': log.title,
            'user': log.user_id,
            'locationLat': log.location.latitude,
            'locationLong': log.location.longitude,
            'log_id': log.log_id
        }
        for log in Log.query.filter(Log.user_id == user.user_id,
                                Log.visit_date == unicode(date_of_logs)).all()}

    info = {'date': previous_day.strftime('%A, %B %d, %Y'),
            'logs': logs}

    return jsonify(info)

@app.route('/change-next-day', methods=['POST'])
def change_next_day():

    d = request.form.get('showDate')
    current_date = datetime.strptime(d, '%A, %B %d, %Y')
    next_day = current_date + timedelta(days=1)
    date_of_logs = next_day.strftime('%Y-%m-%d')

    user = User.query.filter(User.username == session['user']).one()

    logs = {
        log.log_id: {
            'locationId': log.location_id,
            'visitDate': log.visit_date,
            'arrived': log.arrived,
            'departed': log.departed,
            'comments': log.comments,
            'title': log.title,
            'user': log.user_id,
            'locationLat': log.location.latitude,
            'locationLong': log.location.longitude,
            'log_id': log.log_id
        }
        for log in Log.query.filter(Log.user_id == user.user_id,
                                Log.visit_date == unicode(date_of_logs)).all()}

    info = {'date': next_day.strftime('%A, %B %d, %Y'),
            'logs': logs}


    return jsonify(info)


@app.route('/location-directory')
def location_directy():
    """List all locations in user's logs"""
    
    user = User.query.filter(User.username == session['user']).one()

    locations = {
        log.location.name+log.location.location_id: {
            'name': log.location.name,
            'address': log.location.address,
            'locationId': log.location.location_id,
            'lat': log.location.latitude,
            'long': log.location.longitude
        }

        for log in Log.query.filter(Log.user_id == user.user_id)
                    .all()}

    return jsonify(locations)

@app.route('/<location_id>')
def get_location_information(location_id):
    """Display logs and location information"""

    user = User.query.filter(User.username == session['user']).one()

    print "******************", type(location_id), location_id

    location_logs = Log.query.filter(Log.user_id == user.user_id, Log.location_id == location_id).all()

    location_info = Location.query.filter(Location.location_id == location_id).one()


    return render_template('location_info.html', location_info=location_info, 
                            location_logs=location_logs)

@app.route('/profile/<username>/view-profile')
def view_profile(username):

    user = User.query.filter(User.username == username).one()

    num_logs = Log.query.filter(Log.user_id == user.user_id).all()
    num_logs = len(num_logs)

    return render_template('view_profile.html', user=user, username=username, num_logs=num_logs)


###################

if __name__ == '__main__':

    connect_to_db(app)
    app.debug = True
    # Use the DebugToolbar
    DebugToolbarExtension(app)
    app.run()