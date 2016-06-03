from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import connect_to_db, db, User, Log, Location, Type, LocationType 
from datetime import datetime, timedelta
import os
from sqlalchemy import or_, func, desc, update
import helper

app = Flask(__name__)
app.secret_key = 'ABC'

def check_login(username, password):
    """Check if username and password match credentials in database"""
    try:
    # if username exists in db, check to see if user-entered username and
    # passwords match. If so, store username and home lat/long in session
        user = User.query.filter(User.username == username).one()
        if user.username == username and user.password == password:
            return 'True'
        else: 
            return 'False'
    except:
        print "I don't know what's happening"
        return 'False'

def check_username_exists(username):

    try:
        User.query.filter(User.username == username).one()
        return 'True'
    except:
        return 'False'


def create_user(args):

    fname = args.get('fname') 
    lname = args.get('lname')
    email = args.get('email')
    username = args.get('createUsername')
    password = args.get('pw')
    date_created = datetime.now()

    # create new field in User table
    user = User(email=email, username=username, 
                password=password, fname=fname, lname=lname,
                date_created=date_created)

    return user

def format_time(log_time):
    log_time_hrs = (log_time[0].split(':'))[0]
    log_time_mins = (log_time[0].split(':'))[1]
    if log_time[1] == 'PM':
        if log_time_hrs != '12':
            log_time_hrs = int(log_time_hrs) + 12
        
    else:
        if log_time_hrs not in ['10', '11', '12']:
            log_time_hrs = '0'+log_time_hrs
        if log_time_hrs == '12' and log_time[1] == 'AM':
            log_time_hrs = '00'

    log_time = '{}:{}'.format(log_time_hrs, log_time_mins)

    print type(log_time)

    return log_time

def format_date(args):
    # if user selects date from dropdown calendar, select logs from that date
    if args.get('dateRequest') == 'datepicker':
        date_of_logs = datetime.strptime(args.get('showDate')[0:15], '%a %b %d %Y').strftime('%Y-%m-%d')
   
   # elif user clicks for previous day's info, calculate previous day's date
    elif args.get('dateRequest') == 'previous':
        d = args.get('showDate')
        current_date = datetime.strptime(d, '%A, %B %d, %Y')
        previous_day = current_date - timedelta(days=1)
        date_of_logs = previous_day.strftime('%Y-%m-%d')

    # elif user clicks for next day's info, calculate next day's date
    elif args.get('dateRequest') == 'next':
        d = args.get('showDate')
        current_date = datetime.strptime(d, '%A, %B %d, %Y')
        next_day = current_date + timedelta(days=1)
        date_of_logs = next_day.strftime('%Y-%m-%d')

    return date_of_logs

def check_overlap_times(logged_times, start_time, end_time):
    for start_end in logged_times:
        # if there are any overlapping times in entries for the day, return False
        if ((start_end[0] <= start_time <= start_end[1]) or (start_end[0] <= end_time <= start_end[1])):
            return 'False'
        elif ((start_time <= start_end[0]) and (end_time >= start_end[1])):
            return 'False'
    return

def format_place_types(l_type):

    l_type = l_type.replace('[', '')
    l_type = l_type.replace(']', '')
    l_type = l_type.replace('"', '')
    l_type = l_type.replace('_', ' ')
    return l_type

def add_location(location):

    # if this location already exists, don't do anything additional to db
    try:
        Location.query.filter(Location.location_id == location.location_id).one()
    # if location does not exist in location table, add new field
    except: 
        db.session.add(location)
        db.session.commit()
    return



if __name__ == '__main__':

    connect_to_db(app)
    app.debug = True