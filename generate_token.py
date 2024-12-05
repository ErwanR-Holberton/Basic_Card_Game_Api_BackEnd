import jwt
from datetime import datetime, timedelta
from App import app

def generate_token(username): #generate Jason Web Token
    return jwt.encode({
        'user': username,
        'exp': datetime.utcnow() + timedelta(days=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return data
    except:
        return None
