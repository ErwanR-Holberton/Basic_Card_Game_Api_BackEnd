from flask import Flask
from flask_cors import CORS
from datetime import timedelta
try:
    from APP_config import SECRET_KEY
except:
    print("Ask Developper for APP_config.py file")
    exit(1)

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict' #use cookies only from self to avoid CSRF
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Set session duration
