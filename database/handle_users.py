from database.decorators import Read_DB, Commit_DB
import bcrypt
import json

@Commit_DB
def create_user(cursor, username, email, password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    SQL_Command = """INSERT INTO users (username, password, salt, email) VALUES (%s, %s, %s, %s)"""
    cursor.execute(SQL_Command, (username, hashed_password, salt, email))
    return True

@Commit_DB
def update_user(cursor, username, email, newpassword, selected_deck, user_id):
    try:
        if newpassword:
            # Si un nouveau mot de passe est fourni, on le met à jour
            salt = bcrypt.gensalt()
            hashed_newpassword = bcrypt.hashpw(newpassword.encode('utf-8'), salt)
            SQL_Command = """UPDATE users SET username = %s, password = %s, salt = %s, email = %s, selected_deck = %s WHERE id = %s"""
            cursor.execute(SQL_Command, (username, hashed_newpassword, salt, email, selected_deck, user_id))
        else:
            # Si aucun nouveau mot de passe n'est fourni, on met à jour seulement les autres champs
            SQL_Command = """UPDATE users SET username = %s, email = %s, selected_deck = %s WHERE id = %s"""
            cursor.execute(SQL_Command, (username, email, selected_deck, user_id))
        return True
    except Exception as e:
        print(f"Erreur lors de la mise à jour de l'utilisateur : {e}")
        return False

@Commit_DB
def delete_user_db(cursor, user_id):
    try:
        SQL_Command = """DELETE FROM users WHERE id = %s"""
        cursor.execute(SQL_Command, (user_id,))
        return True
    except Exception as e:
        print(f'Erreur lors de la suppression du compte utilisateur : {e}')
        return False

@Read_DB
def get_user(cursor, username):
    cursor.execute("SELECT password, salt, email FROM users WHERE username = %s", (username,))
    return cursor.fetchone()

def verify_user(conn, username, password):
    user_data = get_user(conn, username)
    if not user_data:
        return False  # User not found

    stored_hashed_password, stored_salt, email = user_data
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), stored_salt.encode('utf-8'))
    return hashed_password == stored_hashed_password.encode('utf-8')

@Read_DB
def get_user_selected_deck_by_id(cursor, user_id):
    cursor.execute("SELECT selected_deck FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None

@Read_DB
def get_user_id_by_username(cursor, username):
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()  # Fetch the first row
    return result[0] if result else None  # Return the id if it exists, otherwise None

@Read_DB
def get_deck_by_user_id(cursor, user_id):
    cursor.execute("SELECT decks FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    return json.loads(result[0]) if result and result[0] else []
