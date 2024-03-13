import os 

# encapsulate configuration settings for the application 
# by defining settings as class attributes we can easily access and manage them in a structured manner
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # configure db URI for sqlalchemy:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///serencity.db'
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

