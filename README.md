# Serencity Application

Serencity is a web application designed to help users discover and share serene spots in their locality. Leveraging Google Maps and OAuth integration, Serencity provides an interactive platform for exploring and marking out peaceful locations.

## Features

- **Spot Discovery**: Users can explore a variety of serene spots marked on the map.
- **User Authentication**: Secure login/logout functionality with Google OAuth.
- **Spot Management**: Users can add, save, view, and delete their favorite spots.
- **Google Maps Integration**: Interactive map to view and select serene spots.
- **Event Invitations**: Users can send invites for events at their favorite spots via Google Calendar.
- **Responsive Design**: The application is designed to be responsive and user-friendly.

## Installation

To set up Serenity on your local machine, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/yale-cpsc-419-fa23/project-project-group-5.git
   ```
   
2. Install the required dependencies:
  ```bash
   pip install -r requirements.txt
  ```

3. Set up environment variables:
- Create a `.env` file in the root directory.
- Add the necessary configurations (e.g., `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `SECRET_KEY`).

4. Run the application:
  ```bash
  python app.py
  ```

## Setting Up Environment Variables

**Using `.env` File**: Place the following in your `.env` file (this should be a file at the root of your project, not within any folder):

```bash
FLASK_APP=app.py
SECRET_KEY=mysecretkey
DATABASE_URI=sqlite:///instance/serencity.db
GOOGLE_MAPS_API_KEY=your_maps_api_key
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
````

## Steps to Set Environment Variables
- [Steps to get Keys] (https://docs.google.com/document/d/1kUtxLRn5iqxcP2-q2KLt6ZnEpUdv9dgzD7TWDzSeJZc/edit)


## Authors 
Developed over 3 months in CPSC 419 Fall 2023 class. 
- [aileen.siele@yale.edu] (Aileen Siele)
- [basvi.vimbisai@gmail.com] (Vimbisai Basvi)
- [sarah.teng@yale.edu] (Sarah Teng)

## Citations

- [OAuth Authentication with Flask -- GeeksForGeeks](https://www.geeksforgeeks.org/oauth-authentication-with-flask-connect-to-google-twitter-and-facebook/)
- [One to Many Database Relationships](https://www.digitalocean.com/community/tutorials/how-to-use-one-to-many-database-relationships-with-flask-sqlalchemy)
- [Flask-SQLAlchemy Relationships](https://dev.to/freddiemazzilli/flask-sqlalchemy-relationships-exploring-relationship-associations-igo)
- [Geocoding API GoogleMaps](https://developers.google.com/maps/documentation/geocoding)
- [Set up config files](https://docs.google.com/document/d/1d2Sqeza0p0NRnAa0rTzbAyimkjS2C7bM5WLUdD5ZSVk/edit?usp=sharing)
- [Calendar Event Practice](https://github.com/VimBasvi/Calendar-Invite-Test)
