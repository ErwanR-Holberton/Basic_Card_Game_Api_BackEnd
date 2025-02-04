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
def get_message_count_by_topic(cursor, topic_id):
    SQL_Command = """SELECT post_count FROM topic WHERE id = %s"""
    cursor.execute(SQL_Command, (topic_id,))
    return cursor.fetchone()[0]

@Read_DB
def get_messages(cursor, topic_id, page_number=1, limit=10):
    OFFSET = (page_number - 1) * limit
    SQL_Command = """SELECT message.id, message.text, message.created_at, users.username AS username
    FROM message
    JOIN users ON message.user_id = users.id
    WHERE message.topic_id = %s
    ORDER BY message.created_at DESC
    LIMIT %s OFFSET %s"""
    cursor.execute(SQL_Command, (topic_id, limit, OFFSET))
    messages = cursor.fetchall()
    return messages
