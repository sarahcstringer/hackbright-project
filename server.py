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
            session['home_long'] = user.home
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
                            email=email, username=username)



@app.route('/set-home', methods=['POST'])
def set_home():
    """Sets user home location"""

    home_lat = request.form.get('lat')
    home_long = request.form.get('long')


    user = User.query.filter(User.email == session['user']).one()

    session['home_lat'] = home_lat 
    session['home_long'] = home_long

    setattr(user, 'home_lat', home_lat)
    setattr(user, 'home_long', home_long)

    db.session.commit()

    return "True"

@app.route('/profile/<username>')
def profile_page(username):
    """Render profile page"""

    return render_template('profile_page.html', username=username)



###################

if __name__ == '__main__':

    connect_to_db(app)

    app.run()