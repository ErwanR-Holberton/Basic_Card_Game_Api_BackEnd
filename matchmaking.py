from flask_socketio import SocketIO, emit
from flask import request
from database.database import verify_user, create_connection, get_user_selected_deck_by_id, get_user_id_by_username, get_cards_from_deck, get_all_cards, get_effect_cards, get_all_effects
from generate_token import generate_token, verify_token
import random, ast
from Classes.DamageCalculator import DamageCalculator
from Classes.Phase import Phase

socketio = SocketIO()

users = {}  # Stores user states
user_ids = {}
waiting_queue = []  # Queue of users waiting for a match

is_testing = True
testdeck = ["1", "2", "5", "6", "10", "17", "19", "16", "3", "4", "8", "9", "27", "29", "30", "31"]

def filter_cards():
    conn = create_connection()
    cards = get_all_cards(conn)
    conn.close()
    return {
        row[0]: [value for idx, value in enumerate(row) if idx not in [0, 1, 4, 5]]
        for row in cards
    }

def get_card_type1(card_id):
    return loaded_cards[card_id][0]
def get_card_type2(card_id):
    return loaded_cards[card_id][1]

def load_effects():
    conn = create_connection()
    effects = get_all_effects(conn)
    effect_cards = get_effect_cards(conn)
    conn.close()

    effect_by_card = {}
    for card_id, effect_id in effect_cards:
        if card_id not in effect_by_card:
            effect_by_card[card_id] = []
        if effect_id in effects:
            effect_by_card[card_id].append(effects[effect_id])

    return effect_by_card

loaded_cards = filter_cards()
effect_by_card = load_effects()

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
    print(f"get deck {cards}")
    if not cards:
        return ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15" ,"16", "17", "18", "19", "20"]
    return cards

def pick(quantity, cards):
    return cards[:quantity], cards[quantity:]

class Game_Match():
    instances = {} #class variable to store match reference for each player: {player_id: match}
    players = [] #used in instances to store player 1 and player 2

    def __init__(self, p1, p2):
        self.players = [p1, p2]
        self.decks = []
        self.answers = {} #used in instances to store their answers {player_id: 'yes'"or 'no'}
        self.cards_in_hand = [[], []]
        self.cards_in_pile = [[], []]
        self.cards_in_trash = [[], []]
        self.cards_on_board = [[0] * 6, [0] * 6] #index 0-2 Equipement 3-5 Traps | store the id
        self.card_timers = [[None] * 6, [None] * 6]
        self.cards_of_other_player = []
        self.cards_played_this_turn = [[], []] # [card_id, slot, list of effects]
        self.damageCalculator = DamageCalculator()

        self.__class__.instances[p1] = self
        self.__class__.instances[p2] = self

        self.decks.append(get_deck(p1))
        self.decks.append(get_deck(p2))

        self.phase = Phase()
        self.init_decks()

    def init_decks(self):
        #put the cards in the pile and shuffle
        self.cards_in_pile[0] = self.decks[0][:]
        random.shuffle(self.cards_in_pile[0])
        self.cards_in_pile[1] = self.decks[1][:]
        random.shuffle(self.cards_in_pile[1])

    def pick_cards_for_player(self, player_index, quantity):
        print(f"picking {quantity} cards")
        cards_picked, cards_remaining = pick(quantity, self.cards_in_pile[player_index])
        self.cards_in_hand[player_index] += cards_picked
        #socketio.emit('pick_cards', {'cards': cards_picked}, to=self.players[player_index])
        self.cards_in_pile[player_index] = cards_remaining
        return cards_picked

    def start_game(self):
        Q1 = len(self.decks[0])
        Q2 = len(self.decks[1])
        #send players their amount of cards
        socketio.emit('set_deck', {'you': Q1, 'oponent': Q2}, to=self.players[0])
        socketio.emit('set_deck', {'you': Q2, 'oponent': Q1}, to=self.players[1])
        #pick cards
        cards_p1 = self.pick_cards_for_player(0, 7)
        cards_p2 = self.pick_cards_for_player(1, 7)

        print("Starting game hands:")
        print(self.cards_in_hand[0], cards_p1)
        print(self.cards_in_hand[1], cards_p2)
        print("----------")
        print(self.decks[0])
        print(self.decks[1])
        self.next_phase(self.players[0], self.players[1], cards_p1, cards_p2)

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
            #self.place_cards(cards, player_index, self.cards_of_other_player, other_player_index)
            self.next_phase(player_sid, self.players[other_player_index], cards, self.cards_of_other_player)
        else:
            self.cards_of_other_player = cards

    def card_validation(self, player_sid, card_id, card_slot, phase):
        player_index = self.get_player_index_from_sid(player_sid)
        card_id = card_id.lstrip("0") #input is format "001" and we need "1"

        print(f"card id: {card_id} {int(card_id)}")

        if phase != self.phase.current_phase:
            print("wrong phase")
            return

        if phase != "Preparation" and phase != "Action" and phase != "Discard":
            print("Not prep or action or discard")
            return
        #print("correct phase")

        if card_id not in self.cards_in_hand[player_index]:
            print("card not in hand")
            print(self.cards_in_hand[player_index])
            return
        #print("card in hand")

        card_type = get_card_type1(int(card_id))

        if 0 <= card_slot < 3 and not card_type == "Equipement":
            print("card in slot 0 - 2 not an equipement")
            return
        if 2 < card_slot < 6 and not card_type == "Piège":
            print("card in slot 3 - 6 not a trap")
            return

        if card_slot < 6: #if not action or discard place card on board
            if self.cards_on_board[player_index][card_slot] != 0:
                print("card slot already taken")
                return
            self.cards_on_board[player_index][card_slot] = card_id
            self.card_timers[player_index][card_slot] = 3

        #print("good card")
        self.cards_in_hand[player_index].remove(card_id)
        if 2 < card_slot < 6:
            card_id = -1 # -1 for hidden card cause its a trap

        if card_id != -1:
            card_effects = effect_by_card[int(card_id)]
        if card_type == "Equipement":
            self.apply_effects(player_sid, card_effects)
        if card_slot == 7:
            print("trashing card")
            self.cards_in_trash[player_index].append(card_id)
        if card_slot == 7 or card_type == "Action" or card_type == "Equipement":
            self.cards_played_this_turn[player_index].append([card_id, card_slot, card_effects])
        #print("card effects:", card_effects)

    def place_cards(self, cards_p1, p1_index, cards_p2, p2_index):
        print("dead function called !?")
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

    def check_timers(self, phase):
        if phase != "Action":
            return

        for i in range(len(self.card_timers[0])):
            if self.card_timers[0][i] != None:
                self.card_timers[0][i] -= 1
            if self.card_timers[0][i] == 0:
                card_id = self.cards_on_board[0][i]
                self.cards_in_trash.append(card_id)
                self.cards_on_board[0][i] = 0

        for i in range(len(self.card_timers[1])):
            if self.card_timers[1][i] != None:
                self.card_timers[1][i] -= 1
            if self.card_timers[1][i] == 0:
                card_id = self.cards_on_board[1][i]
                self.cards_in_trash.append(card_id)
                self.cards_on_board[1][i] = 0

    def apply_effects(self, player_sid, effects):
        player_index = player_sid == self.players[1]
        for effect in effect_by_card[3]:
            if effect[2] == 'self':
                target = player_index
            elif effect[2] == 'enemy':
                target = 1 - player_index
            self.damageCalculator.Add_To_Stat(target, effect[0], effect[1])

    def resolve(self):
        p1_bonus_atk = 0
        p1_bonus_def = 0
        p2_bonus_atk = 0
        p2_bonus_def = 0
        p1_posture = "Attack"
        p2_posture = "Attack"

        if len(self.cards_played_this_turn[0]):
            p1_card = self.cards_played_this_turn[0][0]
            p1_posture = get_card_type2(int(p1_card[0]))
            p1_effect = p1_card[2][0]
            if p1_effect[0] == "attack":
                p1_bonus_atk = p1_effect[1]
            elif p1_effect[0] == "defense":
                p1_bonus_def = p1_effect[1]

        if len(self.cards_played_this_turn[1]):
            p2_card = self.cards_played_this_turn[1][0]
            p2_posture = get_card_type2(int(p2_card[0]))
            p2_effect = p2_card[2][0]
            if p2_effect[0] == "attack":
                p2_bonus_atk = p2_effect[1]
            elif p2_effect[0] == "defense":
                p2_bonus_def = p2_effect[1]

        print(f"p1 {p1_bonus_atk} {p1_bonus_def}")
        print(f"p2 {p2_bonus_atk} {p2_bonus_def}")


        p1_damage, p1_alive = self.damageCalculator.Attack(1, 0, p2_posture, p1_posture, p2_bonus_atk, p1_bonus_def)
        p2_damage, p2_alive = self.damageCalculator.Attack(0, 1, p1_posture, p2_posture, p1_bonus_atk, p2_bonus_def)

        if p1_alive and p2_alive:
            game_status = "Unfinished"
        elif (not p1_alive) and (not p2_alive):
            game_status = "Draw"
        elif p1_alive:
            game_status = "p1 win"
        elif p2_alive:
            game_status = "p2 win"
        return p1_damage, p2_damage, game_status

    def next_phase(self, p1, p2 , cards_p1 = [], cards_p2 = []):
        phase = self.phase.current_phase
        timer = self.phase.timer()

        print(f"cards played this time: {self.cards_played_this_turn}")
        print(f"{cards_p1}, {cards_p2}")
        self.check_timers(phase)

        if p1 == self.players[0]:
            p1_index = 0
            p2_index = 1
        else:
            p1_index = 1
            p2_index = 0

        message1 = {'timer': timer, 'phase': phase }
        message2 = {'timer': timer, 'phase': phase }

        if self.phase.is_phase("Draw"):
            discard_p1, discard_p2 = self.force_discard(p1 == self.players[0])
            if cards_p1 == []:
                cards_p1 = self.pick_cards_for_player(p1_index, 2)
            if cards_p2 == []:
                cards_p2 = self.pick_cards_for_player(p2_index, 2)

            count_discarded_p1 = len(self.cards_played_this_turn[p1_index])
            count_discarded_p2 = len(self.cards_played_this_turn[p2_index])

            message1['your_cards'] = cards_p1
            message2['your_cards'] = cards_p2
            message1['discarded_cards'] = discard_p1
            message2['discarded_cards'] = discard_p2
            message1['count_discarded'] = len(discard_p2) + count_discarded_p2
            message2['count_discarded'] = len(discard_p1) + count_discarded_p1

        #send to the oponent wich card were played
        if self.phase.is_phase("Reveal"):
            message1["cards_to_reveal"] = self.cards_played_this_turn[p2_index]
            message1["own_reveal"] = self.cards_played_this_turn[p1_index]
            message2["cards_to_reveal"] = self.cards_played_this_turn[p1_index]
            message2["own_reveal"] = self.cards_played_this_turn[p2_index]

        if self.phase.is_phase("Resolve"):
            p1_damage, p2_damage, game_status = self.resolve()
            message1["your_damage"] = p1_damage
            message2["your_damage"] = p2_damage
            message1["oponent_damage"] = p2_damage
            message2["oponent_damage"] = p1_damage
            if game_status == "p1 win":
                message1["game_status"] = "you win"
                message2["game_status"] = "you loose"
            elif game_status == "p2 win":
                message2["game_status"] = "you win"
                message1["game_status"] = "you loose"
            else:
                message1["game_status"] = game_status
                message2["game_status"] = game_status


        socketio.emit('next_phase', message1, to=p1)
        socketio.emit('next_phase', message2, to=p2)
        self.cards_played_this_turn = [[], []]

    def force_discard(self, is_p1):
        discard_p1 = []
        discard_p2 = []
        while len(self.cards_in_hand[0]) > 7:
            random_index = random.randint(0, len(self.cards_in_hand[0]) - 1)
            discarded_card = self.cards_in_hand[0].pop(random_index)
            discard_p1.append(discarded_card)


        if len(self.cards_in_hand[1]) > 7:
            random_index = random.randint(0, len(self.cards_in_hand[1]) - 1)
            discarded_card = self.cards_in_hand[1].pop(random_index)
            discard_p1.append(discarded_card)

        if is_p1:
            return discard_p1, discard_p2
        return discard_p2, discard_p1


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
