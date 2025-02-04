from sys import argv
from flask import render_template, request, jsonify, make_response, redirect, url_for, session
from database.database import create_connection, create_user, verify_user, get_all_cards, get_topics, get_topic_count, get_messages, get_message_count_by_topic
import jwt, os
from matchmaking import socketio
if "--local" not in argv:
    from Ngrok_module import Start_Ngrok


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

    conn = create_connection()
    messages = get_messages(conn, topic_id, page, limit)
    total_messages = get_message_count_by_topic(conn, topic_id)
    pages = (total_messages + limit - 1) // limit
    print(pages, total_messages, limit)
    conn.close()

    # Prepare the response
    response = {
        'page': page,
        'pages': pages,
        'messages': [{'id': message[0], 'message': message[1], 'creationDate': message[2], 'author': message[3]} for message in messages]
    }
    print(response['messages'])

    return jsonify(response)

@app.route('/forum/topic/<int:topic_id>', methods=['GET'])
def topic_page(topic_id):
    print("topic:", topic_id)
    return render_template("topic.html", topic_id=topic_id)

@app.route('/forum', methods=['GET'])
def forum_page():
    return render_template("forum.html")

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
    socketio.run(app, port=7115, debug=True)
    #app.run(host='0.0.0.0', port=7115)
