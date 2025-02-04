from database.decorators import Read_DB, Commit_DB

@Commit_DB
def create_topic(cursor, user_id, description, category_id):
    SQL_Command = """INSERT INTO topic (user_id, description, category_id) VALUES (%s, %s, %s)"""
    cursor.execute(SQL_Command, (user_id, description, category_id))
    return cursor.lastrowid

@Commit_DB
def update_topic(cursor, topic_id, user_id, new_description):
    #only update if correct user id
    SQL_Command = """UPDATE topic SET description = %s WHERE id = %s AND user_id = %s"""
    cursor.execute(SQL_Command, (new_description, topic_id, user_id))

    return cursor.rowcount > 0  # Returns True if updated, False if not

@Commit_DB
def delete_topic(cursor, topic_id, user_id):
    SQL_Command = """DELETE FROM topic WHERE id = %s AND user_id = %s"""
    cursor.execute(SQL_Command, (topic_id, user_id))
    return cursor.rowcount > 0

@Read_DB
def get_topic_count(cursor, category):
    SQL_Command = """SELECT topic_count FROM category WHERE id = %s"""
    cursor.execute(SQL_Command, (category,))
    return cursor.fetchone()[0]

@Read_DB
def get_topics(cursor, category_id, page_number=1, limit=10):
    OFFSET = (page_number - 1) * limit
    SQL_Command = """SELECT topic.id, topic.description, topic.post_count, topic.created_at, users.username AS username
    FROM topic
    JOIN users ON topic.user_id = users.id
    WHERE topic.category_id = %s
    ORDER BY topic.created_at DESC
    LIMIT %s OFFSET %s"""
    cursor.execute(SQL_Command, (category_id, limit, OFFSET))
    return cursor.fetchall()
