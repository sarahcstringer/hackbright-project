"""Hackbright Project"""

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import connect_to_db, db, User, Log, Location, Type, LocationType 
from datetime import datetime, timedelta
import os
from sqlalchemy import or_, func, desc, update

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
                            email=email, username=username)

@app.route('/check-username', methods=['POST'])
def check_username():

    username = request.form.get('username')

    try:
        User.query.filter(User.username == username).one()
        return 'True'
    except:
        return 'False'


@app.route('/set-home', methods=['POST'])
def set_home():
    """Sets user home location"""

    home_lat = request.form.get('lat')
    home_long = request.form.get('long')
    home_address = request.form.get('address')
    home_id = request.form.get('home_id')

    user = User.query.filter(User.username == session['user']).one()

    setattr(user, 'home_lat', home_lat)
    setattr(user, 'home_long', home_long)
    setattr(user, 'home_address', home_address)
    setattr(user, 'home_id', home_id)

    db.session.commit()

    user = User.query.filter(User.username == session['user']).one()

    session['home_lat'] = home_lat 
    session['home_long'] = home_long

    return "True"

@app.route('/profile/<username>')
def profile_page(username):
    """Render profile page"""

    current_date = datetime.now().strftime('%A, %B %d, %Y')

    user = User.query.filter(User.username == username).one() 

    return render_template('profile_page.html', 
                            username=username, 
                            user=user,
                            current_date=current_date, 
                            google_location_api=google_location_api)


@app.route('/set-date', methods=['POST'])
def set_date():

    date = request.form.get('date')
    date = datetime.strptime(date, '%A, %B %d, %Y').strftime('%m/%d/%Y')
    session['date'] = date

    return 'true'

@app.route('/profile/<username>/add-location')
def add_location(username):

    user = User.query.filter(User.username == username).one()

    return render_template('add_location.html', user=user)

@app.route('/profile/<username>/view-locations')
def view_locations(username):

    # location_types = 

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
    visit_date = datetime.strptime(request.form.get('date')[0:15], '%a %b %d %Y').strftime('%Y-%m-%d')
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

    logs = [{'locationId': log.location_id,
            'locationName': log.location.name,
            'locationAddress': log.location.address,
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
                                Log.visit_date == unicode(date_of_logs))
                                .order_by(Log.arrived)
                                .all()]
                                
    info = {'date': current_date,
            'logs': logs}

    return jsonify(info)

@app.route('/change-datepicker', methods=['POST'])
def change_datepicker():
    date_of_logs = datetime.strptime(request.form.get('showDate')[0:15], '%a %b %d %Y').strftime('%Y-%m-%d')
   
    user = User.query.filter(User.username == session['user']).one()

    logs = [{'locationId': log.location_id,
            'locationName': log.location.name,
            'locationAddress': log.location.address,
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
                                Log.visit_date == unicode(date_of_logs))
                                .order_by(Log.arrived)
                                .all()]
    date_of_logs = datetime.strptime(date_of_logs, '%Y-%m-%d')
    info = {'date': date_of_logs.strftime('%A, %B %d, %Y'),
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

    logs = [{'locationId': log.location_id,
            'locationName': log.location.name,
            'locationAddress': log.location.address,
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
                                Log.visit_date == unicode(date_of_logs))
                                .order_by(Log.arrived)
                                .all()]

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

    logs = [{'locationId': log.location_id,
            'locationName': log.location.name,
            'locationAddress': log.location.address,
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
                                Log.visit_date == unicode(date_of_logs))
                                .order_by(Log.arrived)
                                .all()]

    info = {'date': next_day.strftime('%A, %B %d, %Y'),
            'logs': logs}


    return jsonify(info)


@app.route('/location-directory')
def location_directory():
    """List all locations in user's logs"""
    
    user = User.query.filter(User.username == session['user']).one()

    locations = {
        log.location.name+log.location.location_id: {
            'name': log.location.name,
            'address': log.location.address,
            'locationId': log.location.location_id,
            'locationName': log.location.name,
            'locationAddress': log.location.address,
            'lat': log.location.latitude,
            'long': log.location.longitude,
            'loc_types': str([loc_type.location_type.type_name.replace('_', ' ') for loc_type in log.location.locationtypes])
        }

        for log in Log.query.filter(Log.user_id == user.user_id)
                    .all()}

    return jsonify(locations)

@app.route('/search-location-directory', methods=['POST'])
def search_location_directory():
    """List all locations in user's logs"""
    
    user = User.query.filter(User.username == session['user']).one()
    search_term = request.form.get('search')

    locations = {
        log.location.name+log.location.location_id: {
            'name': log.location.name,
            'address': log.location.address,
            'locationId': log.location.location_id,
            'locationName': log.location.name,
            'locationAddress': log.location.address,
            'lat': log.location.latitude,
            'long': log.location.longitude,
            'loc_types': str([loc_type.location_type.type_name.replace('_', ' ') for loc_type in log.location.locationtypes])
        }

        for log in db.session.query(Log).join(Location).filter(Log.user_id == user.user_id, func.lower(Location.name).like('%'+search_term+'%'))
                    .all()}

    return jsonify(locations)


@app.route('/profile/location-info/<location_id>')
def get_location_information(location_id):
    """Display logs and location information"""

    user = User.query.filter(User.username == session['user']).one()

    location_logs = Log.query.filter(Log.user_id == user.user_id, Log.location_id == location_id).order_by(desc(Log.visit_date)).all()

    location_info = Location.query.filter(Location.location_id == location_id).one()


    return render_template('location_info.html', location_info=location_info, 
                            location_logs=location_logs)

@app.route('/profile/<username>/view-profile')
def view_profile(username):

    user = User.query.filter(User.username == username).one()

    num_logs = Log.query.filter(Log.user_id == user.user_id).all()
    num_logs = len(num_logs)

    return render_template('view_profile.html', user=user, username=username, num_logs=num_logs)


@app.route('/edit-username-check', methods=['POST'])
def edit_username_check():

    username = request.form.get('username')

    try:
        User.query.filter(User.username == username).one()
        return 'True'
    except:
        return 'False'

@app.route('/add-new-username', methods=['POST'])
def add_new_username():

    new_username = request.form.get('username')
    user = User.query.filter(User.username == session['user']).one()
    user.username = new_username

    db.session.commit()

    print 'I committed a new entry'

    session['user'] = new_username
    print 'I changed the session username to', new_username
    print session['user']

    user = User.query.filter(User.username == new_username).one()

    return jsonify({'user': user.username})

@app.route('/delete-log', methods=['POST'])
def delete_log():
    log_id = request.form.get('logID')
    log_id = int(log_id.replace('log',''))
    log = Log.query.get(log_id)
    db.session.delete(log)
    db.session.commit()
    return 'True'

@app.route('/save-log', methods=['POST'])
def save_log():
    log_id = request.form.get('logID')
    log_id = int(log_id.replace('log',''))
    log = Log.query.get(log_id)
    log.title = request.form.get('newTitle')
    log.comments = request.form.get('newComments')
    visit_date = request.form.get('newDate')
    start_time = request.form.get('newArrival')
    end_time = request.form.get('newDeparture')

    logged_times = db.session.query(Log.arrived, 
                        Log.departed).filter(Log.visit_date == visit_date).all()

    for start_end in logged_times:

        if ((start_end[0] <= start_time <= start_end[1]) or (start_end[0] <= end_time <= start_end[1])):
            return 'False'
        elif ((start_time <= start_end[0]) and (end_time >= start_end[1])):
            return 'False'

    log.visit_date = visit_date
    log.arrived = start_time
    log.departed = end_time
    db.session.commit()

    return 'True'

@app.route('/check-times', methods=['POST'])
def check_times():
    start_time = request.form.get('arrival')
    end_time = request.form.get('departure')
    date = datetime.strptime(request.form.get('date')[0:15], '%a %b %d %Y').strftime('%Y-%m-%d')

    print date

    logged_times = db.session.query(Log.arrived, 
                        Log.departed).filter(Log.visit_date == date).all()

    for start_end in logged_times:
        print start_end
        if ((start_end[0] <= start_time <= start_end[1]) or (start_end[0] <= end_time <= start_end[1])):
            return 'False'
        elif ((start_time <= start_end[0]) and (end_time >= start_end[1])):
            return 'False'

    return 'True'
        



###################

if __name__ == '__main__':

    connect_to_db(app)
    app.debug = True
    # Use the DebugToolbar
    DebugToolbarExtension(app)
    app.run()