from flask_socketio import SocketIO, emit
from flask import request
from database.database import verify_user, create_connection, get_user_selected_deck_by_id, get_user_id_by_username, get_cards_from_deck, get_all_cards
from generate_token import generate_token, verify_token
import random, ast

socketio = SocketIO()

users = {}  # Stores user states
user_ids = {}
waiting_queue = []  # Queue of users waiting for a match

def filter_cards():
    conn = create_connection()
    cards = get_all_cards(conn)
    conn.close()
    return {
        row[0]: [value for idx, value in enumerate(row) if idx not in [0, 1, 4, 5]]
        for row in cards
    }

def test_card_type1(card_id_string, type_string):
    card_id = int(card_id_string)
    return type_string == loaded_cards[card_id][0]

loaded_cards = filter_cards()
print(loaded_cards)
print(test_card_type1("1", "Equipement"))

class Phase:
    def __init__(self):
        self.phases = ["Draw", "Preparation", "Reveal", "Action", "Resolve", "Discard"]
        self.current_index = 0  # Start at the first phase

    def next_phase(self):
        self.current_index = (self.current_index + 1) % len(self.phases)  # Increment and wrap around

    @property
    def current_phase(self):
        return self.phases[self.current_index]  # Return the current phase

    def is_phase(self, phase_name):
        return self.current_phase.lower() == phase_name.lower()  # Case-insensitive comparison


def update_player_status(player, status):
    socketio.emit('status', {'state': status}, to=player)
    users[player] = status

@socketio.on('game_login')
def game_login(data):
    sid = request.sid
    username = data.get('username', None)
    password = data.get('password', None)
    conn = create_connection()
    result = verify_user(conn, username, password)
    if result:
        user_id = get_user_id_by_username(conn, username)
        user_ids[sid] = user_id
        update_player_status(sid, "verified")
    else:
        user_id = None
    conn.close()
    emit('game_login_response', {'user_id': user_id}, to=sid)

def get_deck(sid):
    user_id = user_ids[sid]
    conn = create_connection()
    deck_id = get_user_selected_deck_by_id(conn, user_id)
    string_cards = get_cards_from_deck(conn, deck_id)
    if string_cards is not None:
        print(type(string_cards))
        cards = ast.literal_eval(string_cards)
    else:
        cards = None
    conn.close()
    if not cards:
        return ["2", "4", "6", "8", "10", "12", "14", "16", "18"]
    return cards

def pick(quantity, cards):
    return cards[:quantity], cards[quantity:]

class Game_Match():
    instances = {} #class variable to store match reference for each player: {player_id: match}
    players = [] #used in instances to store player 1 and player 2
    answers = {} #used in instances to store their answers {player_id: 'yes'"or 'no'}
    decks = []
    cards_in_hand = [[], []]
    cards_in_pile = [[], []]
    cards_on_board = [[0] * 6, [0] * 6]
    cards_of_other_player = []

    def __init__(self, p1, p2):
        self.players.append(p1)
        self.players.append(p2)
        self.answers = {}

        self.__class__.instances[p1] = self
        self.__class__.instances[p2] = self

        self.decks.append(get_deck(p1))
        self.decks.append(get_deck(p2))

        self.phase = Phase()
        self.init_decks()
        print("new match", self.players)

    def init_decks(self):
        #put the cards in the pile and shuffle
        self.cards_in_pile[0] = self.decks[0][:]
        random.shuffle(self.cards_in_pile[0])
        self.cards_in_pile[1] = self.decks[1][:]
        random.shuffle(self.cards_in_pile[1])

    def pick_cards_for_player(self, player_index, quantity):
        cards_picked, cards_remaining = pick(quantity, self.cards_in_pile[player_index])
        self.cards_in_hand[player_index] += cards_picked
        socketio.emit('pick_cards', {'cards': cards_picked}, to=self.players[player_index])
        self.cards_in_pile[player_index] = cards_remaining

    def start_game(self):
        Q1 = len(self.decks[0])
        Q2 = len(self.decks[1])
        #send players their amount of cards
        socketio.emit('set_deck', {'you': Q1, 'oponent': Q2}, to=self.players[0])
        socketio.emit('set_deck', {'you': Q2, 'oponent': Q1}, to=self.players[1])
        #pick cards
        self.pick_cards_for_player(0, 5)
        self.pick_cards_for_player(1, 5)

    def are_users_ready(self, sid):
        print(sid, type(sid))
        self.answers[sid] = True
        if len(self.answers) == 2:
            self.answers = {}
            self.start_game()

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
        self.answers[player_id] = response
        if not response: #player said no

            #send the other player back in queue if he didnt answer or accepted
            if other_player not in self.answers or self.answers[other_player]:
                update_player_status(other_player, 'waiting')
                waiting_queue.append(other_player)
                match_users()  # Re-check for matching

            #send player who refused out of the queue
            update_player_status(player_id, 'connected')
            self.delete_match()

        elif response:
            if other_player in self.answers: #both player accepted
                if self.answers[player_id]:
                    self.make_users_load_game()
                    self.answers = {}

    def make_users_load_game(self):
        update_player_status(self.players[0], 'in_match')
        update_player_status(self.players[1], 'in_match')

    def disconnection(self, disconnected_player):
        other_player = self.get_other_player(disconnected_player)
        print("setting other to connected")
        update_player_status(other_player, 'connected')
        self.delete_match()

    def get_player_index_from_sid(self, player_sid):
        if player_sid == self.players[0]:
            return 0
        elif player_sid == self.players[1]:
            return 1
        print("Wrong Sid in phase_validation")
        return None

    def phase_validation(self, player_sid, cards, phase):
        print("Validating phase:", phase)
        player_index = self.get_player_index_from_sid(player_sid)
        for card in cards:
            if card not in self.cards_in_hand[player_index]:
                print(f"Wrong card id, card should not be in user hand: {card}")
                self.phase_response(False, player_sid)
                return
        self.phase_response(True, player_sid)
        self.answers[player_sid] = True
        if len(self.answers) == 2:
            self.answers = {}
            self.phase.next_phase()
            other_player_index = 1 - player_index
            self.place_cards(cards, player_index, self.cards_of_other_player, other_player_index)
            socketio.emit('next_phase', {'timer': 30, 'your_cards':cards, 'oponent_cards':self.cards_of_other_player, 'phase':self.phase.current_phase }, to=player_sid)
            socketio.emit('next_phase', {'timer': 30, 'your_cards':self.cards_of_other_player, 'oponent_cards':cards, 'phase':self.phase.current_phase }, to=self.players[other_player_index])
        else:
            self.cards_of_other_player = cards

    def card_validation(self, player_sid, card_id, card_slot, phase):
        player_index = self.get_player_index_from_sid(player_sid)
        if phase != self.phase.current_phase:
            print("wrong phase")
            return
        print("correct phase")

        if card_id not in self.cards_in_hand[player_index]:
            print("card not in hand")
            print(self.cards_in_hand[player_index])
            return
        print("card in hand")

        if 0 <= card_slot < 3 and not test_card_type1(card_id, "Equipement"):
            print("card in slot 0 - 2 not an equipement")
        if 2 < card_slot < 7 and not test_card_type1(card_id, "Trap"):
            print("card in slot 3 - 6 not a trap")

        print("good card")

    def place_cards(self, cards_p1, p1_index, cards_p2, p2_index):
        for card in cards_p1:
            self.cards_in_hand[p1_index].remove(card)
            self.cards_on_board[p1_index].append(card)

        for card in cards_p2:
            self.cards_in_hand[p2_index].remove(card)
            self.cards_on_board[p2_index].append(card)

    def phase_response(self, is_accepting, player_sid):
        if is_accepting:
            socketio.emit('phase_validation_accepted', {}, to=player_sid)
        else:
            socketio.emit('phase_validation_denied', {}, to=player_sid)

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    update_player_status(sid, 'connected')
    print(sid, "connected")

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    print(sid, "disconnected")

    if sid in users:
        del users[sid]
    if sid in user_ids:
        del user_ids[sid]
    if sid in waiting_queue:
        waiting_queue.remove(sid)
    if sid in Game_Match.instances:
        match = Game_Match.instances[sid]
        match.disconnection(sid)

@socketio.on('start_queue')
def start_queue():
    sid = request.sid
    if users[sid] == 'verified':
        update_player_status(sid, 'waiting')
        waiting_queue.append(sid)
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
    response = data.get('response', False)
    emit('server_recieved_match_response', {}, to=sid)
    match_instance = Game_Match.instances[sid]
    match_instance.user_response_to_matchmaking(sid, response)

@socketio.on('ready_to_start')
def user_says_ready():
    sid = request.sid
    match_instance = Game_Match.instances[sid]
    match_instance.are_users_ready(sid)

@socketio.on('phase_validation')
def phase_validation(data):
    sid = request.sid
    match_instance = Game_Match.instances[sid]
    cards = data['cards']
    phase = data['phase']
    match_instance.phase_validation(sid, cards, phase)

@socketio.on('card_validation')
def card_validation(data):
    sid = request.sid
    match_instance = Game_Match.instances[sid]
    card = data['card']
    slot = data['slot']
    phase = data['phase']
    print(f"received validation {card}, {slot}, {phase}")
    match_instance.card_validation(sid, card, slot, phase)

@socketio.on('player_move')
def player_move(data):
    sid = request.sid
    match_instance = Game_Match.instances[sid]
    position = data['position']
    other_player = match_instance.get_other_player(sid)
    emit('player_move', {'position': position }, to=other_player)


@socketio.on('end_match')
def end_match():
    sid = request.sid
    match_instance = Game_Match.instances[sid]
    update_player_status(match_instance.players[0], 'connected')
    update_player_status(match_instance.players[1], 'connected')
    match_instance.delete_match()
