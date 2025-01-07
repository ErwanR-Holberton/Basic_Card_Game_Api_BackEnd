from flask import render_template, request, jsonify, make_response, redirect, url_for, session
from Ngrok_module import Start_Ngrok
from database.database import create_connection, create_user, verify_user, get_all_cards
import jwt, os
from matchmaking import socketio


from App import app
from generate_token import generate_token
socketio.init_app(app)

def add_cookie_to_render(file, *args, **kwargs):  #you should pass html file name and render arguments
    response = make_response(render_template(file, *args, **kwargs)) # need to add a default page
    response.set_cookie('prev_page', file, httponly=True)
    return response

@app.route('/')
def index():
    return add_cookie_to_render('index.html')

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
    conn.close()
    if result:
        token = generate_token(username)
        response = add_cookie_to_render(previous_page, user=username)
        response.set_cookie('jwt_token', token.decode('utf-8'), httponly=True)  # Set the token in an HTTP-only cookie
        return response
    else:
        return  add_cookie_to_render(previous_page, login_error="Invalid username or password")

@app.route('/signup', methods=['POST'])
def signup():
    previous_page = request.cookies.get('prev_page')
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    conn = create_connection()
    result = create_user(conn, username, email, password)
    conn.close()
    if result:
        token = generate_token(username)
        response = add_cookie_to_render(previous_page, user=username)
        response.set_cookie('jwt_token', token.decode('utf-8'), httponly=True)  # Set the token in an HTTP-only cookie
        return response
    else:
        return  add_cookie_to_render(previous_page, signup_error="Invalid username")

@app.route('/logout', methods=['POST'])
def logout():
    previous_page = request.cookies.get('prev_page')
    response = add_cookie_to_render(previous_page)
    response.set_cookie('jwt_token', '', expires=0)  # Remove the JWT cookie by setting its expiration to the past
    return response

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
        return render_template('deck_builder.html', user=data, cards=cards)
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired!'}), 403 #need to redirect to ligin or do something that makes better sense

@app.route('/get_cards_routes', methods=['GET'])
def get_cards_routes_for_unity():
    conn = create_connection()
    cards = get_all_cards(conn)
    conn.close()
    return [(card[0], card[1], card[2], card[3], card[5]) for card in cards]

#---------------------------------------------

@app.route('/protected', methods=['GET'])
def protected():
    token = request.cookies.get('jwt_token')
    user_data = None
    personnalised_content = None
    if not token:
        return add_cookie_to_render('protected.html', user=None)
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return render_template('protected.html', user=data)
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired!'}), 403 #need to redirect to ligin or do something that makes better sense

#---------------------------------------------

if __name__ == '__main__':
    print("server running...")
    socketio.run(app, port=7115)
    #app.run(host='0.0.0.0', port=7115)
