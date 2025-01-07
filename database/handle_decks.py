from database.decorators import Read_DB, Commit_DB
import json

@Commit_DB
def create_deck(cursor, cards_json):
    insert_query = "INSERT INTO decks (cards) VALUES (%s)"
    cursor.execute(insert_query, (cards_json,))
    return cursor.lastrowid

@Commit_DB
def add_deck_to_user(cursor, user_id, new_deck_id):
    SQL_Command = """
    UPDATE users
    SET decks = JSON_ARRAY_APPEND(decks, '$', %s)
    WHERE id = %s
    AND NOT JSON_CONTAINS(decks, %s);"""
    cursor.execute(SQL_Command, (new_deck_id, user_id, new_deck_id))

@Commit_DB
def remove_deck_from_user(cursor, user_id, deck_id_to_remove):
    cursor.execute("SELECT decks FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()[0]
    deck_list = json.loads(result)
    deck_list.remove(deck_id_to_remove)
    cursor.execute("UPDATE users SET decks = %s WHERE id = %s", (json.dumps(deck_list), user_id))
    return True

@Read_DB
def check_if_deck_exists(cursor, card_id_list):
    SQL_Command = """SELECT COUNT(*) FROM decks WHERE cards = %s;"""
    cursor.execute(SQL_Command, (json.dumps(card_id_list), ))
    result = cursor.fetchone()
    return True

@Read_DB
def get_cards_from_deck(cursor, deck_id):
    SQL_Command = """SELECT cards FROM decks WHERE deck_id = %s;"""
    cursor.execute(SQL_Command, (str(deck_id),))
    result = cursor.fetchone()
    return result[0] if result else None
