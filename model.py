"""Models and database functions for Hackbright project"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

###########################
# Model definitions

class User(db.Model):

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(25), nullable=False )
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(25), nullable=False)
    home_lat = db.Column(db.String(40), nullable=True)
    home_long = db.Column(db.String(40), nullable=True)
    # home_address = db.Column(db.String(25))
    # home_city = db.Column

    def __repr__(self):

        return "<User user_id={}, username={}".format(self.user_id, 
                                                        self.username)

class Location(db.Model):

    __tablename__ = 'locations'

    location_id = db.Column(db.String(40), primary_key=True)
    latitude = db.Column(db.String(40), nullable=False)
    longitude = db.Column(db.String(40), nullable=False)
    address = db.Column(db.String(500), nullable=False)

class Log(db.Model):

    __tablename__ = 'logs'

    log_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), 
                                                        nullable=False)
    location_id = db.Column(db.String(40), db.ForeignKey('locations.location_id'), 
                                                        nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    visit_date = db.Column(db.String(20), nullable=False)
    arrived = db.Column(db.String(20), nullable=False)
    departed = db.Column(db.String(20), nullable=False)
    comments = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(50), nullable=False)

    user = db.relationship('User', backref=db.backref('logs'))

    location = db.relationship('Location', backref=db.backref('logs'))


def connect_to_db(app):

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///locations'
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == '__main__':
    from server import app
    connect_to_db(app)
    db.create_all()
    print "Connected to DB."

