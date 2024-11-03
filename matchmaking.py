from flask_socketio import SocketIO, emit
from flask import request

socketio = SocketIO()

users = {}  # Stores user states
waiting_queue = []  # Queue of users waiting for a match

def update_player_status(player, status):
    socketio.emit('status', {'state': status}, to=player)
    users[player] = status


class Game_Match():
    instances = {} #stores match reference for each player: {player_id: match}
    players = [] #used in instances to store player 1 and player 2
    answers = {} #used in instances to store their answers {player_id: 'yes'"or 'no'}
    def __init__(self, p1, p2):
        self.players.append(p1)
        self.players.append(p2)
        self.answers = {}
        self.__class__.instances[p1] = self
        self.__class__.instances[p2] = self
        print("new match", self.players)

    def delete_match(self): #empties the refs in instances
        print("ending match", self.players)
        for player in self.players:
            if player in self.__class__.instances:
                del self.__class__.instances[player]
        self.players.clear()

    def get_other_player(self, player1):
        #returns the player2 id
        return self.players[0] if player1 != self.players[0] else self.players[1]

    def user_response_to_matchmaking(self, player_id, response):
        other_player = self.get_other_player(player_id)
        if response == 'no':
            self.answers[player_id] = 'no'

            #send the other player back in queue if he didnt answer or accepted
            if other_player not in self.answers or self.answers[other_player] == 'yes':
                update_player_status(other_player, 'waiting')
                waiting_queue.append(other_player)
                match_users()  # Re-check for matching

            #send player who refused out of the queue
            update_player_status(player_id, 'connected')
            self.delete_match()

        elif response == 'yes':
            self.answers[player_id] = 'yes'
            if other_player in self.answers:
                if self.answers[player_id] == 'yes':
                    update_player_status(player_id, 'in_match')
                    update_player_status(other_player, 'in_match')

    def disconnection(self, disconnected_player):
        other_player = self.get_other_player(disconnected_player)
        update_player_status(other_player, 'connected')
        self.delete_match()

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    users[sid] = 'connected'
    print(sid, "connected")
    emit('status', {'state': 'connected'}, to=sid)

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    print(sid, "disconnected")

    if sid in users:
        del users[sid]
    if sid in waiting_queue:
        waiting_queue.remove(sid)
    if sid in Game_Match.instances:
        match = Game_Match.instances[sid]
        match.disconnection(sid)


@socketio.on('start_queue')
def start_queue():
    sid = request.sid
    users[sid] = 'waiting'
    waiting_queue.append(sid)
    emit('status', {'state': 'waiting'}, to=sid)
    match_users()

def match_users():
    print("checking queue:", waiting_queue)
    if len(waiting_queue) >= 2:

        player1 = waiting_queue.pop(0) # Take two first users from the queue
        player2 = waiting_queue.pop(0)

        users[player1] = 'prompt_users' # Update user states
        users[player2] = 'prompt_users'

        # Send prompt to both players
        emit('prompt_match', {'message': 'Do you want to enter a match?', 'timer': 30}, to=player1)
        emit('prompt_match', {'message': 'Do you want to enter a match?', 'timer': 30}, to=player2)

        print("starting match:", player1, player2)
        Game_Match(player1, player2)

@socketio.on('match_response')
def handle_match_response(data):
    sid = request.sid
    response = data.get('response', 'no')
    emit('server_recieved_match_response', {}, to=sid)
    match_instance = Game_Match.instances[sid]
    match_instance.user_response_to_matchmaking(sid, response)

@socketio.on('end_match')
def end_match():
    sid = request.sid
    match_instance = Game_Match.instances[sid]
    update_player_status(match_instance.players[0], 'connected')
    update_player_status(match_instance.players[1], 'connected')
    match_instance.delete_match()
