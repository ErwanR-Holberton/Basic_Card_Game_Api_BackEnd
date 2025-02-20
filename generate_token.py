import jwt, os
from datetime import datetime, timedelta
from App import app

def generate_token(username, user_id): #generate Jason Web Token
    return jwt.encode({
        'user': username,
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=6)
        }, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return data
    except:
        return None
