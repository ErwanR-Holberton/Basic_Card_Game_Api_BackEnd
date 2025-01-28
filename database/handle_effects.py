from database.decorators import Read_DB, Commit_DB

@Commit_DB
def create_effect(cursor, stat, value, target):
    SQL_Command = """ INSERT INTO effect (stat, value, target) VALUES (%s, %s, %s)"""
    cursor.execute(SQL_Command, (stat, value, target))
    return True

@Commit_DB
def create_effect_card(cursor, card_id, effect_id):
    SQL_Command = """ INSERT INTO effect_card (card_id, effect_id) VALUES (%s, %s)"""
    cursor.execute(SQL_Command, (card_id, effect_id,))
    return True

@Read_DB
def get_all_effects(cursor):
    SQL_Command = """SELECT * FROM effect"""
    cursor.execute(SQL_Command)
    effects = cursor.fetchall()
    return {effect[0]: effect[1:] for effect in effects}

@Read_DB
def get_effect_cards(cursor):
    SQL_Command = """SELECT * FROM effect_card"""
    cursor.execute(SQL_Command)
    return cursor.fetchall()
