from database.decorators import Read_DB, Commit_DB
import bcrypt

@Commit_DB
def create_user(cursor, username, email, password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    SQL_Command = """INSERT INTO users (username, password, salt, email) VALUES (%s, %s, %s, %s)"""
    cursor.execute(SQL_Command, (username, hashed_password, salt, email))
    return True

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
