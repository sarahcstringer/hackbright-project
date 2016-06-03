"""Hackbright Project"""

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import connect_to_db, db, User, Log, Location, Type, LocationType 
from datetime import datetime, timedelta
import os
from sqlalchemy import or_, func, desc, update
import helper

app = Flask(__name__)

#for debug toolbar
app.secret_key = 'ABC'

# create global API key for google maps API (*currently not using key in app*)
google_api = os.environ['GOOGLE_LOC_API']
global google_location_api
google_location_api = "https://maps.googleapis.com/maps/api/js?key="+google_api+"&libraries=places&callback=initialize"

app.jinja_env.undefined = StrictUndefined

@app.context_processor
def inject_google_api():
    """Create global variable to use in base html for google map API credentials"""
    return dict(google_location_api=google_location_api)

@app.route('/')
def homepage():
    """Render homepage template if no user in session, redirect user to profile if logged in"""

    #if user in session, redirect to profile page
    try: 
        session['user']
        return redirect('/profile/'+session['user'])

    #otherwise, render the homepage.html template
    except:
        return render_template('homepage.html')

@app.route('/check-login', methods=['POST'])
def check_login():
    """Check if username and password match user credentials in database"""

    # # collect username and password from post request
    username = request.form.get('username')
    password = request.form.get('password')

    if helper.check_login(username, password) == 'True':
        # add user info to session
        user = User.query.filter(User.username == username).one()
        session['user'] = username
        session['home_lat'] = user.home_lat 
        session['home_long'] = user.home_long
        return 'True'
    else:
        return 'False'


@app.route('/logout')
def logout():
    """Delete username from session, flash logout message and redirect to homepage"""

    flash('Successfully logged out')
    session.pop('user')
    return redirect('/')


@app.route('/create-profile', methods=['POST'])
def create_profile():
    """Create profile for user"""

    # receive information via POST request from signup form
    form_args = request.form

    user = helper.create_user(form_args)

    # add and commit
    db.session.add(user)
    db.session.commit()

    # store username in session
    session['user'] = user.username

    return render_template('profile.html', fname=user.fname, lname=user.lname,
                            username=user.username)

@app.route('/check-username', methods=['POST'])
def check_username():
    """Check to see if username is already in database"""
    
    username = request.form.get('username')
    return helper.check_username_exists(username)

@app.route('/set-home', methods=['POST'])
def set_home():
    """Set user home location"""

    home_lat = request.form.get('lat')
    home_long = request.form.get('long')
    home_address = request.form.get('address')
    home_id = request.form.get('home_id')

    # retrieve user from User table
    user = User.query.filter(User.username == session['user']).one()

    # set user attributes
    setattr(user, 'home_lat', home_lat)
    setattr(user, 'home_long', home_long)
    setattr(user, 'home_address', home_address)
    setattr(user, 'home_id', home_id)

    # commit changes to user
    db.session.commit()

    # add home longitude and latitude to session
    session['home_lat'] = home_lat 
    session['home_long'] = home_long

    return "True"

@app.route('/profile/<username>')
def profile_page(username):
    """Render profile page for specific user"""

    # retrieve user object from database to pass to profile page template
    user = User.query.filter(User.username == username).one() 

    return render_template('profile_page.html', 
                            username=username, 
                            user=user)


@app.route('/set-date', methods=['POST'])
def set_date():
    """Get date of the logs the user is currently viewing, store in session"""

    # if there is a value for "date" in the post data, retrieve that
    if request.form.get('date'):
        date = request.form.get('date')
    # otherwise, use today's date
    else: 
        date = datetime.now().strftime('%A, %B %d, %Y')
    # format date
    date = datetime.strptime(date, '%A, %B %d, %Y').strftime('%m/%d/%Y')
    
    # store that date in session info
    session['date'] = date

    return 'true'

@app.route('/profile/<username>/add-location')
def add_location(username):
    """Render template for page to add a location/log"""

    user = User.query.filter(User.username == username).one()

    return render_template('add_location.html', user=user)

@app.route('/profile/<username>/view-locations')
def view_locations(username):
    """View a user's directory of locations they've visited"""

    return render_template('view_locations.html')

@app.route('/log-new-location', methods=['POST'])
def log_new_location():
    """Create new log in database from user entry"""

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

    # retrieve user from db
    user = User.query.filter(User.username == session['user']).one()


    # # create new location object
    location = Location(location_id=location_id, latitude=latitude,
                        longitude=longitude, address=address, name=name,
                        website=website, phone=phone)
    helper.add_location(location)

    # Clean up the string list of establishment types
    for l_type in place_types:
        l_type = helper.format_place_types(l_type)

        try:
            Type.query.filter(Type.type_name == l_type).one()
        # if it doesn't, add it to the table
        except: 
            add_location_type = Type(type_name=l_type)
            db.session.add(add_location_type)
            db.session.commit()
            
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

@app.route('/check-times', methods=['POST'])
def check_times():
    """Check if times for a log do not overlap with other logs on that day"""
    
    # get information about log
    start_time = request.form.get('arrival')
    end_time = request.form.get('departure')
    date = datetime.strptime(request.form.get('date')[0:15], '%a %b %d %Y').strftime('%Y-%m-%d')

    # query database for logs matching that date
    logged_times = db.session.query(Log.arrived, 
                        Log.departed).filter(Log.visit_date == date).all()

    # loop through the logs on that day and get their start/end times
    if helper.check_overlap_times(logged_times, start_time, end_time) == 'False':
        return 'False'

    return 'True'

@app.route('/change-time-range', methods=['POST'])
def change_time_range():
    """Return logs that match a given user-entered time range"""

    # get date the user is viewing and string format
    d = request.form.get('showDate')
    
    if not d:
        d = datetime.now().strftime('%A, %B %d, %Y')

    current_date = datetime.strptime(d, '%A, %B %d, %Y')
    date_of_logs = current_date.strftime('%Y-%m-%d')
   
    # get user information
    user = User.query.filter(User.username == session['user']).one()

    start_time = request.form.get('startTime').split(' ')
    print "****", start_time
    start_time = helper.format_time(start_time)
    print start_time

    end_time = request.form.get('endTime').split(' ')
    end_time = helper.format_time(end_time)


    # query database and create list of logs matching filters
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
        # filter for user's logs matching date and in between specificed time range
        for log in Log.query.filter(Log.user_id == user.user_id,
                                Log.visit_date == unicode(date_of_logs),
                                Log.arrived <= end_time,
                                Log.departed >= start_time)
                                .order_by(Log.arrived)
                                .all()]

    date_of_logs = datetime.strptime(date_of_logs, '%Y-%m-%d')
    
    # create dictionary to jsonify and return to browser
    info = {'date': date_of_logs.strftime('%A, %B %d, %Y'),
            'logs': logs}

    return jsonify(info)


@app.route('/load_today')
def load_today():
    """Load today's information"""

    # get current date
    current_date = datetime.now().strftime('%A, %B %d, %Y')
    date_of_logs = datetime.now().strftime('%Y-%m-%d')

    # get information about user
    user = User.query.filter(User.username == session['user']).one()

    # query database and create list of logs matching filters
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

    # create dictionary to jsonify and return to browser                            
    info = {'date': current_date,
            'logs': logs}

    return jsonify(info)

@app.route('/change-date', methods=['POST'])
def change_date():
    """Return logs for specified date"""

    date_of_logs = helper.format_date(request.form)

    # retrieve user's info
    user = User.query.filter(User.username == session['user']).one()

    # format start time
    start_time = request.form.get('startTime').split(' ')
    start_time = helper.format_time(start_time)
    
    # # format end time
    end_time = request.form.get('endTime').split(' ')
    end_time = helper.format_time(end_time)

    # retrieve logs that match database query
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
                                Log.visit_date == unicode(date_of_logs),
                                Log.arrived <= end_time,
                                Log.departed >= start_time)
                                .order_by(Log.arrived)
                                .all()]
    # format date to display on page
    date_of_logs = datetime.strptime(date_of_logs, '%Y-%m-%d')
    
    # create dictionary to pass to browser
    info = {'date': date_of_logs.strftime('%A, %B %d, %Y'),
            'logs': logs}

    return jsonify(info)


@app.route('/location-directory')
def location_directory():
    """List all locations in user's logs"""
    
    user = User.query.filter(User.username == session['user']).one()

    # query database for list of all locations a user has visited
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
    
    # get user information
    user = User.query.filter(User.username == session['user']).one()
    
    # retrieve user's search term
    search_term = request.form.get('search')

    # query database for location names matching that search term
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
        for log in db.session.query(Log).join(Location)
                        .filter(Log.user_id == user.user_id, 
                        func.lower(Location.name).like('%'+search_term+'%'))
                        .all()}

    return jsonify(locations)


@app.route('/profile/location-info/<location_id>')
def get_location_information(location_id):
    """Display logs and location information for given location and user"""

    # get user info
    user = User.query.filter(User.username == session['user']).one()

    # get list of logs a person has created for a given location
    location_logs = Log.query.filter(Log.user_id == user.user_id, Log.location_id == location_id).order_by(desc(Log.visit_date)).all()

    # get details about location from Location table
    location_info = Location.query.filter(Location.location_id == location_id).one()


    return render_template('location_info.html', location_info=location_info, 
                            location_logs=location_logs)

@app.route('/profile/<username>/view-profile')
def view_profile(username):
    """Retrieve information about user to display on view_profile page"""

    # retrieve user information
    user = User.query.filter(User.username == username).one()
    user_start_date = user.date_created
    user_start_date= user_start_date.strftime('%m/%d/%Y')

    # retrieve number of logs user has created
    num_logs = len(Log.query.filter(Log.user_id == user.user_id).all())

    return render_template('view_profile.html', user_start_date=user_start_date,
                            user=user, username=username, num_logs=num_logs)


@app.route('/edit-username-check', methods=['POST'])
def edit_username_check():
    """check if username the user requests already exists in database"""
    username = request.form.get('username')

    try:
        User.query.filter(User.username == username).one()
        return 'True'
    except:
        return 'False'

@app.route('/add-new-username', methods=['POST'])
def add_new_username():
    """update user's username in database"""

    new_username = request.form.get('username')
    # query for user
    user = User.query.filter(User.username == session['user']).one()
    # set new username for user
    user.username = new_username
    # commit change to database
    db.session.commit()
    # set session with new username
    session['user'] = new_username
    # query for updated user information
    user = User.query.filter(User.username == new_username).one()

    return jsonify({'user': user.username})

@app.route('/delete-log', methods=['POST'])
def delete_log():
    """delete log from database"""

    log_id = request.form.get('logID')
    # get the id of the log to be deleted
    log_id = int(log_id.replace('log',''))
    # query the database for this log
    log = Log.query.get(log_id)
    # delete the log
    db.session.delete(log)
    # commit changes
    db.session.commit()

    return 'True'

@app.route('/save-log', methods=['POST'])
def save_log():
    """save new information about a log that already exists in db"""

    log_id = request.form.get('logID')
    # retrieve log id
    log_id = int(log_id.replace('log',''))
    # retrieve log information from db
    log = Log.query.get(log_id)
    # retrieve information user entered for updated log entry
    log.title = request.form.get('newTitle')
    if request.form['newComments'] != '':
        log.comments = request.form.get('newComments')
    visit_date = request.form.get('newDate')
    start_time = request.form.get('newArrival')
    end_time = request.form.get('newDeparture')

    data = {}

    # query db for the other logs a user has entered for that day to make sure
    # there are no overlapping time entries
    logged_times = db.session.query(Log.arrived, 
                        Log.departed).filter(Log.visit_date == visit_date,
                        Log.log_id != log_id).all()

    if helper.check_overlap_times(logged_times, start_time, end_time) == 'False':
        data['status'] = 'False'
        return

    # if no logs that overlap in time for this day, update details for the log
    log.visit_date = visit_date
    log.arrived = start_time
    log.departed = end_time

    db.session.commit()

    log = Log.query.get(log_id)

    data['status'] = 'True'
    data['title'] = log.title
    data['arrived'] = log.arrived
    data['departed'] = log.departed
    data['comments'] = log.comments
    data['location'] = log.location.name
    data['visited'] = log.visit_date

    return jsonify(data)

@app.route('/test-log-info', methods=['POST'])
def test_log_info():
    start_date = request.form.get('startDate')
    end_date = request.form.get('endDate')


    start_date = datetime.strptime(start_date, '%m/%d/%Y')
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%m/%d/%Y')
    end_date = end_date + timedelta(days=1)
    end_date = end_date.strftime('%Y-%m-%d')

    num_logs = {}
    this_day = start_date
    data_dict = {
        'labels': [],
        'datasets': [
            {
                # 'label': 'Test',
                "fillColor": "rgba(220,220,220,0.2)",
                "strokeColor": "rgba(220,220,220,1)",
                "pointColor": "rgba(220,220,220,1)",
                "pointStrokeColor": "#fff",
                "pointHighlightFill": "#fff",
                "pointHighlightStroke": "rgba(220,220,220,1)",
                'data': []
            }
        ]

    }

    while this_day != end_date:

        num_logs_this_day = db.session.query(func.count(Log.log_id)).filter(Log.visit_date==this_day).all()
        num_logs[this_day] = int(num_logs_this_day[0][0])


        this_day = datetime.strptime(this_day, '%Y-%m-%d')
        this_day = this_day + timedelta(days=1)
        this_day = this_day.strftime('%Y-%m-%d')

    for key in sorted(num_logs.keys()):
        data_dict['labels'].append(key)
        data_dict['datasets'][0]['data'].append(num_logs[key])

    return jsonify(data_dict)


###################

if __name__ == '__main__':

    connect_to_db(app)
    # app.debug = True
    # Use the DebugToolbar
    # DebugToolbarExtension(app)
    app.run()