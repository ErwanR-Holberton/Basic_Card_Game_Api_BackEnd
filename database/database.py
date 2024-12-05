try:
    from database.DB_config import host, user, password, database
except:
    print("Ask Developper for DB_Config file")
    exit(1)

import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from database.handle_users import *
from database.handle_cards import *
from database.handle_decks import *

def create_connection():
    """Create a database connection."""
    try:
        conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
        print("Connection successful!")
        return conn
    except Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        exit(1)



if __name__ == "__main__":
    main()
