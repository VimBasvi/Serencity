import os
import base64


#!/usr/bin/env python3
from datetime import datetime, timedelta
from flask import Flask, render_template, session
from flask_talisman import Talisman
from flask_sqlalchemy import SQLAlchemy
from flask_googlemaps import GoogleMaps
from flask import redirect, url_for, flash, request, jsonify, send_file
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from io import BytesIO

# from flask_migrate import Migrate


# might become useful in future
# from werkzeug.security import generate_password_hash

# session magement. common tasks of logging in and ot, and remembering users'
# sessions over extended periods
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user,login_required
#bring in config file -- configure settings like api keys etc
from config import Config
# simplifies OAuth and OAuth2 integrations  - create instance of class and
# register OAuth provider, eg Google
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

# called before creating flask app instance
load_dotenv()

# init flask app
app = Flask(__name__)

# config keys in terminal before running app
app.config.from_object(Config)
# init db  with sqlalchemy
db = SQLAlchemy(app)
# migrate = Migrate(app, db)

# Init flask-login's loginManager
login_manager = LoginManager()
login_manager.init_app(app)

# # init oauth objs from authlib lib
oauth = OAuth(app)

def generate_nonce(length=32):
    '''generate ...'''
    return base64.urlsafe_b64encode(os.urandom(length)).rstrip(b'=').decode('utf-8')

@app.route('/logout')
def logout():
    '''logout users'''
    # rmv user's session by logging them out
    session.pop('token', None)
    logout_user() # cookie, session and token cleanup
    # flash msge when logout is successful
    flash('You have successfully logged out of your Serencity account.', 'success')
    
    # redirect to home pg 
    return redirect(url_for('show_map'))

# use login manager to load user from the db
@login_manager.user_loader
def load_user(user_id):
    '''load user from database'''
    return db.session.get(User, int(user_id))

# Define a custom Jinja2 filter for Base64 encoding
@app.template_filter('b64encode')
def b64encode_filter(data):
    '''define custom Jinja2 filter for Base64 encoding'''
    if data:
        return base64.b64encode(data).decode('utf-8')  # Encode the binary data to Base64
    return None  # Return None if no data is provided

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
def fetchLocationsFromSQLite():
    '''Function to fetch spot data from SQLite table'''
    spots = Spot.query.all()
    locations = []
    for spot in spots:
        location = {
            'name': spot.name,
            'latitude': spot.latitude,
            'longitude': spot.longitude,
            'approx_address': spot.approx_adress,
            'notes': spot.notes,
            'user_id': spot.user_id,
        }
        locations.append(location)
    return locations

def fetchCurrentUserLocationsFromSQLite(current_user_id):
    '''Function to fetch spot data from SQLite table for the current user'''
    spots = Spot.query.filter_by(user_id=current_user_id).all()
    locations = []
    for spot in spots:
        location = {
            'name': spot.name,
            'latitude': spot.latitude,
            'longitude': spot.longitude,
            'approx_address': spot.approx_adress,
            'notes': spot.notes,
            'user_id': spot.user_id,
            'id': spot.id,
        }
        locations.append(location)
    return locations

# def sent invites table

# def received invites table

# def mailbox table - combo of received invites and sent invites

def init_oauth():
    ''' Define Google's OAuth 2.0 server'''
    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    # Access env vars in one's flask app:
    google_client_id = app.config['GOOGLE_CLIENT_ID']
    google_client_secret = app.config['GOOGLE_CLIENT_SECRET']
    # credentials used to identofy our application to Google:
    oauth.register(
        name='google',
        client_id=google_client_id,
        client_secret=google_client_secret,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile https://www.googleapis.com/auth/calendar.events'
        }
    )
init_oauth()

@app.route('/')
def index():
    ''' Handle requests to root URL and return response '''
    return render_template('index.html', current_user=current_user)

@app.route('/auth')
def auth():
    ''' Handle requests to root URL and return response '''
    return render_template('auth.html')


@app.route('/google')
def google_login():
    ''' Redirect to Google's OAuth 2.0 server'''
    # Generate nounce to associate with this authentication req
    nonce = generate_nonce()
    session['oauth_nonce'] = nonce
    # Redirect to google_auth function - set up OAUth flow
    # when route is visited, it redirects user to g's  oauth server,
    # asking for the permissions defined in the scope
    redirect_uri = url_for('google_auth_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri,nonce=nonce)
# 2 calls
# user clicks login- redirected to google page
# Google sends info to callback with a token
# Go back to google to verify the token, it's valid or invalid,
# # if it is then we want to store in db

@app.route('/callback')
def google_auth_callback():
    # handle callback from Google's OAuth server
    # retrieve userdetails from Google
    # Check if 'code' is in the request form
    if 'code' not in request.args:
        # Handle the missing 'code' case thru redirect and flash
        flash('Authentication error: missing authorization code.', 'error')
        return redirect(url_for('map'))

    token = oauth.google.authorize_access_token()
    session['token'] = token
    print(token)
    # retrieve nonce from session
    nonce = session.get('oauth_nonce', '')
    # Check if nonce in session and in the ID token match
    if not nonce:
        flash('Authentication err. Please try again', 'error')
        return redirect(url_for('map'))
    try:
        user_info = oauth.google.parse_id_token(token, nonce=nonce)
    except Exception as err:
        flash(f'Error parsing ID token: {err}', 'error')
        return redirect(url_for('map'))
    finally:
        session.pop('oauth_nonce', None)
    # Check if user exists in db
    user = User.query.filter_by(email=user_info['email']).first()
    # if user doesn't exist. create new user
    if not user:
        user = User(
            name=user_info['name'],
            email=user_info['email'],
            profile_pic=user_info['picture']) # check if picture exists or not
        db.session.add(user)
        db.session.commit()
    # Log user in using Flask-Login
    login_user(user)
    #redirect to map page aft login
    return redirect('/map')

@app.route('/map')
def show_map():
    '''render map '''
    locations = fetchLocationsFromSQLite() or []
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    return render_template('/map.html',api_key=api_key,locations=locations)


# user can see all their spots on this dashboard
# separate displaying the invite page and  sending invite make diff functs
@app.route('/invite', methods=['GET', 'POST'])
@login_required
def invite():
    ''' displays invite pg '''
    if request.method == 'POST':
        # Extract form data
        event_name = request.form.get('eventname')
        location = request.form.get('location')
        date = request.form.get('date')
        time = request.form.get('time')
        emails = request.form.get('emails')
        description = request.form.get('description')

        # Prepare the event data
        attendees = [{'email': email.strip()} for email in emails.split(',')]
        # Parsing the start datetime
        start_datetime_str = f"{date} {time}"
        # Parsing the start datetime
        start_datetime_obj = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M")
        start_datetime = start_datetime_obj.isoformat() + 'Z'  # 'Z' indicates UTC time

        # Parsing the end datetime and assuming 1 hour event duration
        end_datetime_str = f"{date} {time}"
        end_datetime = (
            datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M") + timedelta(hours=1)
        ).isoformat() + 'Z'

        # take location details:
        spot = Spot.query.get(location)
        if not spot:
            flash("Selected location is invalid", "error")
            return redirect(url_for('invite'))

        # concatenate spot name and address for event location
        event_location = f"{spot.name}, {spot.approx_adress}"
        
        
        event_body = {
            'summary': event_name,
            'location': event_location,
            'description': description,
            'start': {'dateTime': start_datetime, 'timeZone': 'UTC'},
            'end': {'dateTime': end_datetime, 'timeZone': 'UTC'},
            'attendees': attendees,
        }
        print(event_body)

        # Create the event on Google Calendar
        creds = Credentials(
            token=session['token'].get('access_token'),
            refresh_token=session['token'].get('refresh_token'),
            token_uri=session['token'].get('token_uri'),
            client_id=session['token'].get('client_id'),
            client_secret=session['token'].get('client_secret'),
            scopes=['https://www.googleapis.com/auth/calendar.events']
        )
        service = build('calendar', 'v3', credentials=creds)
        event = service.events().insert(calendarId='primary', body=event_body).execute()

        return 'Invite Sent!'
    else:
        # GET request - Show the invite creation form
        spots = Spot.query.all()
        
        return render_template('invite.html', spots=spots)

@app.route('/add_spot')
@login_required
def map():
    ''' displays the map in /add_spot'''
    address_error_msg = request.args.get('address_error_msg')
    if address_error_msg is None:
        address_error_msg = ''

    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    return render_template('/add_spot.html', api_key=api_key,address_error_msg=address_error_msg)

@app.route('/add_spot', methods=['POST'])
def add_spot():
    '''add spot to the database'''
    address_error_msg = ""
    name = request.form['name']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    address = request.form['address']
    # specific_directions = request.form['descri']
    notes = request.form['description']
    image = request.files['spotImage']
    audio_file = request.files['audioFile']
    # Save the image to a folder or database

    #error handling for if no address
    if latitude is None or longitude is None or latitude == '' or longitude == '':
        address_error_msg="Address is required"
        return redirect(url_for('add_spot', address_error_msg=address_error_msg))
    # Handle invalid float conversion or empty strings
    try:
        latitude = float(latitude) if latitude else None
        longitude = float(longitude) if longitude else None
    except ValueError:
        latitude = None
        longitude = None

    #check for audio file (optional) and read into binary data
    if image:
        image_binary = image.read()
        print("image received")
    else:
        image_binary = None  # Set a default value if no image was uploaded
    #check for audio file (optional) and read into binary data
    if audio_file:
        audio_binary = audio_file.read()
    else:
        audio_binary = None

    # Create a new Spot instance
    new_spot = Spot(name=name, latitude=latitude, longitude=longitude,
                    approx_adress=address, notes=notes, user_id=current_user.id,
                    image=image_binary, audio=audio_binary)
    # Add new spot to the database
    db.session.add(new_spot)
    db.session.commit()
    return redirect(url_for('add_spot'))  # Redirect to map

@app.route('/my_spots')
@login_required
def myspots():
    '''Display spots added by user, with option to view saved spots'''
    user_id = current_user.id
    view_mode = request.args.get('view', 'all')  # 'all' or 'saved'
    if view_mode == 'saved':
        results = SavedSpots.query.filter_by(user_id=user_id)  #retrieves only the saved spots
    else:
        results = Spot.query.filter_by(user_id=user_id)  # retrieves all spots
    locations = fetchCurrentUserLocationsFromSQLite(user_id)
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    return render_template('my_spots.html', api_key=api_key,
                           results=results, user_name=current_user.name,
                           locations=locations, view_mode=view_mode)




@app.route('/is-spot-saved/<int:spot_id>', methods=['GET'])
@login_required
def is_spot_saved(spot_id):
    '''check whether spot has already been saved'''
    user_id = current_user.id
    existing_spot = SavedSpots.query.filter_by(user_id=user_id,
                                               spot_id=spot_id).first()
    return jsonify({'is_saved': existing_spot is not None})

@app.route('/save-spot/<int:spot_id>', methods=['POST'])
@login_required
def save_spot(spot_id):
    '''save spots'''
    user_id = current_user.id
    spot = Spot.query.get(spot_id)


    if not spot:
        return jsonify({'error': 'Spot not found'}), 404

    try:
        existing_spot = SavedSpots.query.filter_by(user_id=user_id,
                                                   spot_id=spot_id,
                                                   name=spot.name).first()
        if existing_spot:
            # Toggle save/unsave
            db.session.delete(existing_spot)
            # db.session.commit()
            # return jsonify({'saved': False, 'message': 'Spot unsaved successfully'})
        else:
            new_saved_spot = SavedSpots(user_id=user_id,
                                    spot_id=spot_id,
                                    name=spot.name,
                                    saved_at=datetime.utcnow())
            db.session.add(new_saved_spot)
        db.session.commit()

        return jsonify({'saved': not existing_spot, 'message': 'Spot saved successfully' if not existing_spot else 'Spot unsaved successfully'})

    except Exception as e:
        db.session.rollback()
        # Log the exception for debugging
        print(str(e))
        return jsonify({'error': 'An error occurred while saving the spot'}), 500


  
@app.route('/delete_spot/<int:spot_id>', methods=['POST'])
@login_required
def delete_spot(spot_id):
    '''find spot by ID and delete it if saved, otherwise delete from spots'''
    user_id = current_user.id
    # .filter(YourModel.field1 == 'value1' & YourModel.field2 == 'value2').all()
    # Check if the spot is saved by the user
    saved_spot = SavedSpots.query.filter_by(user_id=user_id, spot_id=spot_id).first()

    # If saved, delete from SavedSpots
    if saved_spot:
        db.session.delete(saved_spot)

    # Check if the spot exists in the Spot table
    spot_to_delete = Spot.query.get(spot_id)
    if spot_to_delete:
        db.session.delete(spot_to_delete)
        db.session.commit()
        return jsonify({'deleted': True})
    else:
        db.session.commit()  # Commit only the saved spot was deleted
        return jsonify({'deleted': False, 'error': 'Spot not found'})


# user can see spot details once you click on spot:
@app.route('/spot/<int:spot_id>')
def spot_details(spot_id):
    '''display spot details'''
    saved_spot = SavedSpots.query.get(spot_id)
    spot = Spot.query.get(spot_id)
    if spot is None:
        abort(404)  # Spot not found, return a 404 error
    # Pass the spot details to the template to display
    image_data = None
    if spot.image:
        image_data = spot.image  # Assuming spot.image holds the binary image data
    audio_data = None
    if spot.audio:
        audio_data = spot.audio
    return render_template('spot_details.html',
                           spot=spot,
                           image_data=image_data,
                           audio_data=audio_data)


@app.route('/privacy-policy')
def privacy_policy():
    '''privacy policy'''
    return render_template('privacy.html')

@app.route('/terms-of-service')
def terms_of_service():
    '''terms of service'''
    return render_template('service.html')

if __name__ =='__main__':
    # create db tables if they don't exist
    # specify which app we are referring to and the
    # context we're running in - app context or request
    # context( holds data on who made req and the data within req)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
