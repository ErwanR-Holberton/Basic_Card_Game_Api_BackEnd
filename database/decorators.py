from mysql.connector import Error

# create a Decorator to handle connection and cursor
def Commit_DB(func):
    def wrapper(conn, *args, **kwargs):
        cursor = None
        try:
            cursor = conn.cursor()
            result = func(cursor, *args, **kwargs)
            conn.commit()# Commit if everything is fine
            return result
        except Error as e:
            print(f"Error catched by the Commit wrapper: {e}")
            conn.rollback()  # Rollback in case of an error
            return None
        except Exception as e:
            print(f"Error catched by the Commit wrapper: {e}")
            conn.rollback()  # Rollback in case of an error
            raise e
        finally:
            if cursor:
                cursor.close()  # Ensure the cursor is closed
    return wrapper

# create a Decorator to handle connection and cursor
def Read_DB(func):
    def wrapper(conn, *args, **kwargs):
        cursor = None
        try:
            cursor = conn.cursor()
            result = func(cursor, *args, **kwargs)
            return result
        except Error as e:
            print(f"Error catched by the Read wrapper: {e}")
            return None
        finally:
            if cursor:
                cursor.close()  # Ensure the cursor is closed
    return wrapper
