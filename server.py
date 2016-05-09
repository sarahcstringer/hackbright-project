"""Hackbright Project"""

from flask import Flask, render_template, redirect, request, flash, session
from jinja2 import StrictUndefined
from model import connect_to_db, db, User, Log

app = Flask(__name__)

#for debug toolbar
app.secret_key = 'ABC'

app.jinja_env.undefined = StrictUndefined


@app.route('/')
def homepage():

    return render_template('homepage.html')

@app.route('/signup')
def signup():

    return render_template('signup.html')

@app.route('/check-username', methods=['POST'])
def check_username():
    """Checks to see if username is unique"""

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

    session['user'] = email
    print session['user']
    return render_template('profile.html', fname=fname, lname=lname,
                            email=email, username=username)



@app.route('/set-home', methods=['POST'])
def set_home():
    """Sets user home location"""

    home_lat = request.form.get('lat')
    home_long = request.form.get('long')


    user = User.query.filter(User.email == session['user']).one()

    setattr(user, 'home_lat', home_lat)
    setattr(user, 'home_long', home_long)

    db.session.commit()

    return "True"

@app.route('/profile')
def profile_page():
    """Render profile page"""

    return render_template('profile_page.html')



###################

if __name__ == '__main__':

    connect_to_db(app)

    app.run()