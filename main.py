from sys import argv
from flask import render_template, request, jsonify, make_response, redirect, url_for, session
from database.database import *
from App import csrf
import jwt, os, re
from matchmaking import socketio
if "--local" not in argv:
    from Ngrok_module import Start_Ngrok


from App import app
from generate_token import generate_token
socketio.init_app(app)

def add_cookie_to_render(file, *args, **kwargs):  #you should pass html file name and render arguments
    response = make_response(render_template(file, *args, **kwargs)) # need to add a default page
    response.set_cookie('prev_page', file, httponly=True, secure=True, samesite='Strict')
    return response

@app.route('/')
def index():
    token = request.cookies.get('jwt_token')
    if token:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return add_cookie_to_render('index.html', user=data.get('user'), user_id=data.get('user_id'))

    return add_cookie_to_render('index.html', user=None)

@app.route('/status')
def status():
    return "ok"

@app.route('/login', methods=['POST'])
def login():
    previous_page = request.cookies.get('prev_page')
    username = request.form['username']
    password = request.form['password']
    conn = create_connection()
    result = verify_user(conn, username, password)
    user_id = get_user_id_by_username(conn, username)
    conn.close()
    if result:
        token = generate_token(username, user_id)
        response = add_cookie_to_render(previous_page, user=username, user_id=user_id)
        response.set_cookie('jwt_token', token.decode('utf-8'), httponly=True, secure=True)  # Set the token in an HTTP-only cookie
        return response
    else:
        return  add_cookie_to_render(previous_page, login_error="Invalid username or password")

@app.route('/signup', methods=['POST'])
def signup():
    previous_page = request.cookies.get('prev_page')
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']

    # Vérification des entrées avec regex
    if not is_valid_username(username):
        return add_cookie_to_render(previous_page, signup_error="Invalid username format")
    if not is_valid_email(email):
        return add_cookie_to_render(previous_page, signup_error="Invalid email format")
    if not is_valid_password(password):
        return add_cookie_to_render(previous_page, signup_error="Weak password: 8+ chars, 1 uppercase, 1 number, 1 special char")

    conn = create_connection()
    result = create_user(conn, username, email, password)
    user_id = get_user_id_by_username(conn, username)
    conn.close()

    if result:
        token = generate_token(username, user_id)
        response = add_cookie_to_render(previous_page, user=username, user_id=user_id)
        response.set_cookie('jwt_token', token, httponly=True, secure=True)
        return response
    else:
        return add_cookie_to_render(previous_page, signup_error="Username already taken")

@app.route('/update_user', methods=['POST'])
def update_user_route():
    token = request.cookies.get('jwt_token')
    if not token:
        return add_cookie_to_render('index.html', user=None)

    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        previous_page = request.cookies.get('prev_page')
        username = request.form.get('username')
        oldpassword = request.form.get('oldpassword', "").strip()
        newpassword = request.form.get('newpassword', "").strip()
        confirmpassword = request.form.get('confirmpassword', "").strip()
        selecteddeck = request.form.get('selecteddeck', None)
        email = request.form.get('email')

        # Validation des inputs
        if username and not is_valid_username(username):
            return "Invalid username format", 400
        if email and not is_valid_email(email):
            return "Invalid email format", 400
        if newpassword and not is_valid_password(newpassword):
            return "Weak password: 8+ chars, 1 uppercase, 1 number, 1 special char", 400
        if selecteddeck and not is_safe_input(selecteddeck):
            return "Invalid deck name", 400

        # Vérification des mots de passe si remplis
        if newpassword and oldpassword and newpassword != confirmpassword:
            return "New passwords do not match", 400

        conn = create_connection()
        response = update_user(conn, username, email, oldpassword, newpassword, selecteddeck, data.get('user_id'))
        conn.close()

        if response:
            return add_cookie_to_render(previous_page, username=username, user_id=data.get('user_id'), usermail=email, selected_deck=selecteddeck)
        else:
            return "Update failed", 500

    except jwt.ExpiredSignatureError:
        return add_cookie_to_render('index.html', user=None)
    except jwt.InvalidTokenError:
        return add_cookie_to_render('index.html', user=None)
    except Exception as e:
        print(f"Erreur lors de la mise à jour : {e}")
        return "Internal server error", 500


@app.route('/logout', methods=['POST'])
def logout():
    previous_page = request.cookies.get('prev_page')
    response = add_cookie_to_render(previous_page)
    response.set_cookie('jwt_token', '', expires=0)  # Remove the JWT cookie by setting its expiration to the past
    return response

#---------------------------------------------

@app.route('/deck_builder', methods=['GET'])
def deck_builder():
    token = request.cookies.get('jwt_token')
    user_data = None
    conn = create_connection()
    cards = get_all_cards(conn)
    conn.close()
    if not token:
        return add_cookie_to_render('deck_builder.html', user=None, cards=cards)
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return render_template('deck_builder.html', user=data.get('user'), cards=cards, user_id=data.get('user_id'))
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired!'}), 403 #need to redirect to ligin or do something that makes better sense

@app.route('/get_cards_routes', methods=['GET'])
def get_cards_routes_for_unity():
    conn = create_connection()
    cards = get_all_cards(conn)
    conn.close()
    return [(card[0], card[1], card[2], card[3], card[5]) for card in cards]


# Route to get topics with pagination
@app.route('/forum/topics', methods=['GET'])
def get_topics_route():
    # Get pagination parameters from query parameters
    category = request.args.get('category', default=1, type=int)  # Default to category page 1
    page = request.args.get('page', default=1, type=int)  # Default to page 1
    limit = request.args.get('limit', default=10, type=int)  # Default to 10 topics per page

    print("recieved:", category, page, limit)
    # Ensure limit and page are positive integers
    if page < 1 or limit < 1:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    # Fetch topics from the database (using the defined function)
    conn = create_connection()
    topics = get_topics(conn, category, page, limit)
    total_topics = get_topic_count(conn, category)
    pages = (total_topics + limit - 1) // limit
    print(pages, total_topics, limit)
    conn.close()

    # Prepare the response
    response = {
        'page': page,
        'pages': pages,
        'topics': [{'id': topic[0], 'title': topic[1], 'replies': topic[2], 'creationDate': topic[3], 'author': topic[4]} for topic in topics]
    }
    return jsonify(response)

# Route to get messages with pagination
@app.route('/forum/messages', methods=['GET'])
def get_messages_route():
    # Get pagination parameters from query parameters
    topic_id = request.args.get('topic_id', default=1, type=int)  # Default to category page 1
    page = request.args.get('page', default=1, type=int)  # Default to page 1
    limit = request.args.get('limit', default=10, type=int)  # Default to 10 messages per page

    print("recieved:", topic_id, page, limit)
    # Ensure limit and page are positive integers
    if page < 1 or limit < 1:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    # Fetch messages from the database (using the defined function)
    conn = create_connection()
    messages = get_messages(conn, category, page, limit)
    total_messages = get_topic_count(conn, category)
    pages = (total_messages + limit - 1) // limit
    print(pages, total_messages, limit)
    conn.close()

    # Prepare the response
    response = {
        'page': page,
        'pages': pages,
        'messages': [{'id': message[0], 'title': message[1], 'replies': message[2], 'creationDate': message[3], 'author': message[4]} for message in messages]
    }
    return jsonify(response)

@app.route('/forum/topic/<int:topic_id>', methods=['GET'])
def topic_page(topic_id):
    print("topic:", topic_id)
    return render_template("topic.html", topic_id=topic_id)

@app.route('/forum', methods=['GET'])
def forum_page():
    token = request.cookies.get('jwt_token')
    if token:
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            return render_template("forum.html", user=data.get('user'), user_id=data.get('user_id'))
        except jwt.ExpiredSignatureError:
            return add_cookie_to_render('index.html', user=None)
        except jwt.InvalidTokenError:
            return add_cookie_to_render('index.html', user=None)
    else:
        return render_template("forum.html", user=None)

@app.route("/profil/<int:user_id>", methods=['GET'])
def profil_page(user_id):
    token = request.cookies.get('jwt_token')
    if not token:
        return add_cookie_to_render('index.html', user=None)  # Redirect to index if no token
    try:
        # Décodage du token JWT
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        # Connexion and get decks and id_user
        conn = create_connection()
        logged_in_user_id = get_user_id_by_username(conn, data.get("user"))  # ID user
        user_decks = get_deck_by_user_id(conn, user_id=user_id)
        usermail = get_user(conn, data.get('user'))[2]
        selected_deck = get_user_selected_deck_by_id(conn, user_id=user_id)
        conn.close()
        # User verification
        if logged_in_user_id != user_id:
            return add_cookie_to_render('index.html', user=data)
        return render_template("profil.html", user=data.get('user'), user_id=data.get('user_id'), all_decks=user_decks, selected_deck=selected_deck, username=data.get("user"), usermail=usermail)
    except jwt.ExpiredSignatureError:
        return add_cookie_to_render('index.html', user=None)
    except jwt.InvalidTokenError:
        return add_cookie_to_render('index.html', user=None)

@app.route('/rules', methods=['GET'])
def rules():
    token = request.cookies.get('jwt_token')
    if not token:
        return add_cookie_to_render('rules.html', user=None)
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return render_template('rules.html', user=data.get('user'), user_id=data.get('user_id'))
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired!'}), 403 #need to redirect to ligin or do something that makes better sense


@app.route('/protected', methods=['GET'])
def protected():
    token = request.cookie.get('jwt_token')
    user_data = None
    personnalised_content = None
    if not token:
        return add_cookie_to_render('protected.html', user=None)
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return render_template('protected.html', user=data)
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired!'}), 403 #need to redirect to ligin or do something that makes better sense


def is_valid_username(username):
    return bool(re.match(r'^[a-zA-Z0-9_]{3,20}$', username))

def is_valid_email(email):
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

def is_valid_password(password):
    return bool(re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password))

def is_safe_input(user_input):
    return not bool(re.search(r'[<>]', user_input))  # Empêche les balises HTML/JS

#---------------------------------------------

if __name__ == '__main__':
    print("server running...")
    socketio.run(app, port=7115, debug=True)
    #app.run(host='0.0.0.0', port=7115)
