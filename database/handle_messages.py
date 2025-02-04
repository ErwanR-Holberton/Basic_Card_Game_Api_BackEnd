from database.decorators import Read_DB, Commit_DB

@Commit_DB
def create_message(cursor, user_id, topic_id, text):
    # Insert message
    SQL_Command = """INSERT INTO message (user_id, topic_id, text) VALUES (%s, %s, %s)"""
    cursor.execute(SQL_Command, (user_id, topic_id, text))
    return cursor.lastrowid  # Returns new message ID

@Commit_DB
def update_message(cursor, message_id, user_id, new_text):
    SQL_Command = """UPDATE message SET text = %s WHERE id = %s AND user_id = %s"""
    cursor.execute(SQL_Command, (new_text, message_id, user_id))
    return cursor.rowcount > 0  # True if updated, False if not

@Commit_DB
def delete_message(cursor, message_id, user_id, topic_id):
    SQL_Command = """DELETE FROM message WHERE id = %s AND user_id = %s"""
    cursor.execute(SQL_Command, (message_id, user_id))
    return cursor.rowcount > 0

@Read_DB
def get_messages_after(cursor, topic_id, last_created_at=None, limit=10):
    SQL_Command = """SELECT * FROM message
    WHERE topic_id = %s
    AND (%s IS NULL OR created_at < %s)
    ORDER BY created_at DESC
    LIMIT %s"""
    cursor.execute(SQL_Command, (topic_id, last_created_at, last_created_at, limit))
    messages = cursor.fetchall()
    return messages
