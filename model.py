"""Models and database functions for Hackbright project"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import or_, func, desc, update
from datetime import datetime, timedelta

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
    home_address = db.Column(db.String(250), nullable=True)
    home_id = db.Column(db.String(100), nullable=True)
    date_created = db.Column(db.DateTime, nullable=False)

    def __repr__(self):

        return "<User user_id={}, username={}".format(self.user_id, 
                                                        self.username)

class Location(db.Model):

    __tablename__ = 'locations'

    location_id = db.Column(db.String(100), primary_key=True)
    latitude = db.Column(db.String(40), nullable=False)
    longitude = db.Column(db.String(40), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(100), nullable = False)
    website = db.Column(db.String(200))
    phone = db.Column(db.String(200))

    def __repr__(self):

        return "<Location location_name={}, address={}".format(self.name, self.address)


class Log(db.Model):

    __tablename__ = 'logs'

    log_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), 
                                                        nullable=False)
    location_id = db.Column(db.String(100), db.ForeignKey('locations.location_id'), 
                                                        nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    visit_date = db.Column(db.String(50), nullable=False)
    arrived = db.Column(db.String(20), nullable=False)
    departed = db.Column(db.String(20), nullable=False)
    comments = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(50), nullable=False)

    user = db.relationship('User', backref=db.backref('logs'))

    location = db.relationship('Location', backref=db.backref('logs'), 
                                order_by='desc(Location.name)')

    def __repr__(self):

        return "<Log title: {}, created on{}".format(self.title, self.created_at)


############### useful if wanting to do something with establishment types in the future; 
# not currently using the Type and LocationType tables
class Type(db.Model):

    __tablename__ = 'types'

    type_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    type_name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):

        return "<Location type {}".format(self.type_name)

class LocationType (db.Model):

    __tablename__ = 'location_types'

    loc_type_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    location_id = db.Column(db.String(100), db.ForeignKey('locations.location_id'),
                                            nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('types.type_id'), nullable=False)

    location = db.relationship('Location', backref=db.backref('locationtypes'), 
                            order_by='desc(Location.name)')

    location_type = db.relationship('Type', backref=db.backref('locationtypes'))

    def __repr__(self):

        return "<Location type {} for {}".format(self.type_id, self.location_id)

def example_data():
    user1 = User(email='bbuilder@gmail.com', fname='Bob', lname='Builder',
                username='bbuild', password='password', home_lat='37.794434',
                home_long='-122.39520160000001', 
                home_address='50 Market St, San Francisco, CA 94105, USA',
                home_id='ARi1KXmVCb5Rc', 
                date_created=datetime.strptime('2016-05-19 16:13:42.940831', 
                    '%Y-%m-%d %H:%M:%S.%f'))
    db.session.add(user1)
    db.session.commit()
    user_id = db.session.query(User.user_id).filter(User.username == 'bbuild').one()

    location1 = Location(location_id='ChIJOWCTNGSAhYARLxosf_Izuy4', 
                latitude='37.7936231', longitude='-122.39299269999998',
                address='8 Mission St, San Francisco, CA 94105, USA', 
                name='Hotel Vitale', 
                website='http://www.jdvhotels.com/hotels/california/san-francisco-hotels/hotel-vitale',
                phone='(415) 278-3700')

    db.session.add(location1)
    db.session.commit()

    log1 = Log(user_id=user_id[0], location_id='ChIJOWCTNGSAhYARLxosf_Izuy4', 
                created_at=datetime.strptime('2016-05-29 14:08:51.615528', 
                    '%Y-%m-%d %H:%M:%S.%f'), 
                visit_date='2016-05-29', arrived='16:00', departed='17:00',
                comments='Lovely wedding', title='Wedding')


    db.session.add(log1)
    db.session.commit()



def connect_to_db(app, db_uri='postgresql:///locations'):

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    # app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == '__main__':
    from server import app
    connect_to_db(app)
    db.create_all()
    print "Connected to DB."

