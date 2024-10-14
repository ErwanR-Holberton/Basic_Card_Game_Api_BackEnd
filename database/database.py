import mysql.connector
from mysql.connector import Error
import bcrypt
try:
    from decorators import Read_DB, Commit_DB
except:
    from database.decorators import Read_DB, Commit_DB
from werkzeug.security import generate_password_hash, check_password_hash
try:
    try:
        from database.DB_config import host, user, password, database
    except:
        from DB_config import host, user, password, database
except:
    print("Ask Developper for DB_Config file")
    exit(1)

def create_connection():
    """Create a database connection."""
    try:
        conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
        print("Connection successful!")
        return conn
    except Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        exit(1)

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

def main():
    """Main function to create a database."""
    conn = create_connection()
    create_user(conn, "test4", "mail4", "thisisapassword")
    if verify_user(conn, "test2", "this_is_a_password"):
        print("Password correct")
    else:
        print("Password not correct")
    conn.close()

if __name__ == "__main__":
    main()
