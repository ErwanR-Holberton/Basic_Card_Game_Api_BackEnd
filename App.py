from flask import Flask, request, make_response
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
import secrets

try:
    from APP_config import SECRET_KEY
except:
    print("Ask Developper for APP_config.py file")
    exit(1)

app = Flask(__name__, static_url_path='/static')
csrf = CSRFProtect(app)
CORS(
    app,
    methods=["GET", "POST"],  # Autoriser seulement ces méthodes
    allow_headers=["Content-Type", "Authorization"],
)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_COOKIE_SAMESITE"] = (
    "Strict"  # use cookies only from self to avoid CSRF
)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)  # Set session duration

# Définition de la Content Security Policy
@app.after_request
def add_security_headers(response):
    nonce = secrets.token_hex(16)  # Génère un nonce aléatoire
    response.headers["Content-Security-Policy"] = (
        f"default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}' https://accounts.google.com https://cdn.jsdelivr.net/npm/jwt-decode/;"
        f"style-src 'self' 'unsafe-inline'; "
        f"img-src 'self' data:; "
        f"font-src 'self'; "
        f"object-src 'none'; "
        f"frame-ancestors 'none';"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
