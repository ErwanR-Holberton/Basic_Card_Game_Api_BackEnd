import jwt
from datetime import datetime, timedelta
from App import app
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

def generate_token(username, user_id): #generate Jason Web Token
    return jwt.encode({
        'user': username,
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=6)
        }, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Vérifie et décode un JWT"""
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return data  # Contient {'user': ..., 'user_id': ..., 'exp': ...}
    except ExpiredSignatureError:
        return {'error': 'Token expiré'}
    except InvalidTokenError:
        return {'error': 'Token invalide'}
