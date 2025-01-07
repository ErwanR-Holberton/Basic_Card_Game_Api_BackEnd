from database.decorators import Read_DB, Commit_DB

@Commit_DB
def create_card(cursor, name, type1, type2, description, image_binary):
    SQL_Command = """ INSERT INTO cards (name, type, type2, description, image) VALUES (%s, %s, %s, %s, %s)"""
    cursor.execute(SQL_Command, (name, type1, type2, description, image_binary))
    return True

@Read_DB
def get_all_cards(cursor):
    SQL_Command = """SELECT * FROM cards"""
    cursor.execute(SQL_Command)
    cards = cursor.fetchall()

    new_cards = []
    for card in cards:
        new_cards.append([card[0], card[1], card[2], card[3], card[4], "Cards/New_Small/" + card[1] + ".png"])
        #print(new_cards[-1])
    return new_cards

@Read_DB
def verify_all_ids_in_DB(cursor, card_id_list):
    unique_card_ids = set(card_id_list)
    format_strings = ','.join(['%s'] * len(unique_card_ids))  # Create end of the query
    query = f"SELECT COUNT(*) FROM cards WHERE id IN ({format_strings})"
    cursor.execute(query, tuple(unique_card_ids))
    count = cursor.fetchone()[0]
    return count == len(unique_card_ids)# Check if the count matches the number of IDs checked
