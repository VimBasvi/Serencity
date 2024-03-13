from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db  # Import the SQLAlchemy instance
# def User model - store relevant user info
# col for oauth and isoauth , flask authenticate  --

class User(UserMixin, db.Model):
    '''User Class'''
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    email = db.Column(db.String(256), unique=True)
    profile_pic = db.Column(db.String(512))
    # Relationships
    # one to many relationship with spot model
    # one id will be connected to multiple spots in the spot model
    spots = db.relationship('Spot', back_populates='added_by', lazy=True)
    saved_spots = db.relationship('SavedSpots', back_populates='user', lazy=True)
    #sent_invites =
    '''
    Side note:
    SQL translation: yes, id - email cols but not spots 
    In spots model would be user_id (foreign key) column. It references User's id col 
    '''
# def spot model for db for spots user enters
class Spot(db.Model):
    """spot model for db for spots user enters"""
    __tablename__ = 'spot'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    picture_url = db.Column(db.String(255)) # photos table one to many relationship with a spot
    audio = db.Column(db.BLOB) # one audio
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    approx_adress = db.Column(db.String(255), nullable=False) #
    # specfic directions form user i think?
    specific_directions = db.Column(db.Text)
    # extra notes from user uploading spot? -- okay do we wnna delete?
    # add column to include descripters  like bench, tree, walk way
    notes = db.Column(db.Text)
    # time spot was added
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    # foreign key column for the 'added_by' relationship
    # this links to the User table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    place_id = db.Column(db.String(255)) # store place id for more detail restrieval just in case
    image = db.Column(db.BLOB) #image
    # Relationships
    # Relationship with User model, the back_populates should match the
    # relationship name given in User model.
    # make sure we remember user who entered the spot
    # confusing --- rel btwn added by(someone found the spot and is sharing it) and saved by
    added_by = db.relationship('User', back_populates='spots')
    saved_by = db.relationship('SavedSpots', back_populates='spot', lazy='dynamic') # items not to be loaded immediately,
    #instead cn provide query to further reload later

# def savedspots table
class SavedSpots(db.Model):
    __tablename__ = 'saved_spot'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('spot.id'), nullable=False)
    name = db.Column(db.String(255))
    # time the data was saved:
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    user = db.relationship('User', back_populates='saved_spots')
    spot = db.relationship('Spot', back_populates='saved_by')
# Function to fetch spot data from SQLite table spots
# returns a dictionary named 'locations'

# def sent invites table

# def received invites table

# def mailbox table - combo of received invites and sent invites